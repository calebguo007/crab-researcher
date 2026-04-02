"""
CrabRes Growth Playbooks — 深度执行链

不再输出"建议"，而是输出可执行的剧本（Playbook）。
每个 Playbook 是一条完整的增长路径，展开成 Phase → Step 的 SOP。

例如"KOL 博主种草"不是一句话，而是 22 步 SOP：
  定义画像 → 搜索候选 → 分层外联 → 寄样管理 → 内容追踪 → ROI 计算 → 迭代
"""

import json
import time
import uuid
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class PlaybookStep:
    """Playbook 中的一个执行步骤"""
    order: int = 0
    title: str = ""
    detail: str = ""                  # 具体描述（3-5 句话）
    tools: list[str] = field(default_factory=list)  # 推荐工具
    templates: list[str] = field(default_factory=list)  # 内嵌模板（邮件/表格/文案）
    budget: str = "$0"
    duration: str = ""                # "30 min" / "2 hours" / "1 day"
    output: str = ""                  # 这一步完成后的产出物
    success_criteria: str = ""        # 怎么判断做对了
    common_mistakes: list[str] = field(default_factory=list)
    status: str = "pending"           # pending / in_progress / done / skipped
    result_notes: str = ""            # 用户完成后的笔记


@dataclass
class PlaybookPhase:
    """Playbook 的一个阶段"""
    name: str = ""                    # "准备期" / "执行期" / "追踪期"
    duration: str = ""                # "Day 1-3"
    steps: list[PlaybookStep] = field(default_factory=list)


@dataclass
class Playbook:
    """一条完整的增长执行链"""
    id: str = field(default_factory=lambda: f"pb-{uuid.uuid4().hex[:8]}")
    name: str = ""                    # "KOL 博主种草"
    description: str = ""
    suitable_for: str = ""            # "有实物产品、预算 $500-5K"
    phases: list[PlaybookPhase] = field(default_factory=list)
    total_budget: str = ""
    expected_timeline: str = ""
    expected_results: str = ""
    risk_factors: list[str] = field(default_factory=list)
    priority: int = 0                 # Agent 推荐的优先级 (1=最高)
    status: str = "draft"             # draft / active / completed / abandoned
    created_at: float = field(default_factory=time.time)
    activated_at: Optional[float] = None

    @property
    def total_steps(self) -> int:
        return sum(len(p.steps) for p in self.phases)

    @property
    def completed_steps(self) -> int:
        return sum(1 for p in self.phases for s in p.steps if s.status == "done")

    @property
    def progress_pct(self) -> int:
        total = self.total_steps
        if total == 0:
            return 0
        return round(self.completed_steps / total * 100)


class PlaybookStore:
    """Playbook 持久化存储"""

    def __init__(self, base_dir: str = ".crabres/memory"):
        self.base_dir = Path(base_dir)
        (self.base_dir / "playbooks").mkdir(parents=True, exist_ok=True)

    def _playbooks_path(self) -> Path:
        return self.base_dir / "playbooks" / "all_playbooks.json"

    def _load_all(self) -> list[dict]:
        path = self._playbooks_path()
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    def _save_all(self, data: list[dict]):
        self._playbooks_path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str)
        )

    async def save_playbook(self, playbook: Playbook) -> str:
        """保存或更新一个 Playbook"""
        all_pb = self._load_all()
        pb_dict = asdict(playbook)

        # 更新已存在的，或追加新的
        found = False
        for i, existing in enumerate(all_pb):
            if existing.get("id") == playbook.id:
                all_pb[i] = pb_dict
                found = True
                break
        if not found:
            all_pb.append(pb_dict)

        self._save_all(all_pb)
        logger.info(f"Saved playbook {playbook.id}: {playbook.name} ({playbook.total_steps} steps)")
        return playbook.id

    async def get_playbooks(self, status: str = None) -> list[dict]:
        all_pb = self._load_all()
        if status:
            all_pb = [p for p in all_pb if p.get("status") == status]
        return all_pb

    async def get_playbook(self, playbook_id: str) -> Optional[dict]:
        for p in self._load_all():
            if p.get("id") == playbook_id:
                return p
        return None

    async def activate_playbook(self, playbook_id: str):
        all_pb = self._load_all()
        for p in all_pb:
            if p.get("id") == playbook_id:
                p["status"] = "active"
                p["activated_at"] = time.time()
                break
        self._save_all(all_pb)

    async def update_step_status(self, playbook_id: str, phase_idx: int, step_idx: int, status: str, notes: str = ""):
        all_pb = self._load_all()
        for p in all_pb:
            if p.get("id") == playbook_id:
                try:
                    step = p["phases"][phase_idx]["steps"][step_idx]
                    step["status"] = status
                    if notes:
                        step["result_notes"] = notes
                except (IndexError, KeyError):
                    pass
                break
        self._save_all(all_pb)

    async def get_active_playbook_summary(self) -> str:
        """获取当前活跃 Playbook 的摘要文本，供 Coordinator prompt 注入"""
        active = await self.get_playbooks(status="active")
        if not active:
            return ""

        lines = ["## ACTIVE GROWTH PLAYBOOKS"]
        for pb in active[:3]:
            name = pb.get("name", "")
            phases = pb.get("phases", [])
            total = sum(len(ph.get("steps", [])) for ph in phases)
            done = sum(1 for ph in phases for s in ph.get("steps", []) if s.get("status") == "done")
            pct = round(done / total * 100) if total else 0

            lines.append(f"\n### {name} ({pct}% complete, {done}/{total} steps)")

            # 找到下一个待做的 step
            for ph in phases:
                for s in ph.get("steps", []):
                    if s.get("status") == "pending":
                        lines.append(f"**Next step:** {s.get('title', '')}")
                        lines.append(f"Detail: {s.get('detail', '')[:200]}")
                        break
                else:
                    continue
                break

        return "\n".join(lines)


def parse_playbook_from_llm(raw_json: str) -> Optional[Playbook]:
    """
    从 LLM 输出的 JSON 字符串解析为 Playbook 对象。
    LLM 生成 Playbook 时按照约定格式输出 JSON。
    """
    try:
        data = json.loads(raw_json)
        phases = []
        for ph_data in data.get("phases", []):
            steps = []
            for s_data in ph_data.get("steps", []):
                steps.append(PlaybookStep(
                    order=s_data.get("order", 0),
                    title=s_data.get("title", ""),
                    detail=s_data.get("detail", ""),
                    tools=s_data.get("tools", []),
                    templates=s_data.get("templates", []),
                    budget=s_data.get("budget", "$0"),
                    duration=s_data.get("duration", ""),
                    output=s_data.get("output", ""),
                    success_criteria=s_data.get("success_criteria", ""),
                    common_mistakes=s_data.get("common_mistakes", []),
                ))
            phases.append(PlaybookPhase(
                name=ph_data.get("name", ""),
                duration=ph_data.get("duration", ""),
                steps=steps,
            ))

        return Playbook(
            name=data.get("name", ""),
            description=data.get("description", ""),
            suitable_for=data.get("suitable_for", ""),
            phases=phases,
            total_budget=data.get("total_budget", ""),
            expected_timeline=data.get("expected_timeline", ""),
            expected_results=data.get("expected_results", ""),
            risk_factors=data.get("risk_factors", []),
            priority=data.get("priority", 0),
        )
    except Exception as e:
        logger.error(f"Failed to parse Playbook from LLM output: {e}")
        return None
