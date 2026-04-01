"""
CrabRes Memory System

学习自 Claude Code 的四层记忆架构：
Layer 1: Growth Config（最高优先级，用户配置）
Layer 2: Auto Memory（自动记忆，分类存储）
Layer 3: Session Memory（会话记忆，每次对话摘要）
Layer 4: Growth Dream（后台整理，消除矛盾）

记忆分类（学 Claude Code 的 memdir/）：
- product/    产品 DNA
- goals/      增长目标
- research/   研究数据（竞品/用户画像/渠道）
- strategy/   策略文档（增长计划/内容日历/预算）
- execution/  执行效果（KPI/什么有效/什么无效）
- feedback/   用户修正（偏好/约束/否决）
- journal/    增长日志（每日追加）
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class GrowthMemory:
    """CrabRes 记忆系统"""

    CATEGORIES = ["product", "goals", "research", "strategy", "execution", "feedback", "journal"]

    def __init__(self, base_dir: str = ".crabres/memory"):
        self.base_dir = Path(base_dir)
        self._ensure_dirs()

    def _ensure_dirs(self):
        for cat in self.CATEGORIES:
            (self.base_dir / cat).mkdir(parents=True, exist_ok=True)

    async def save(self, key: str, data: Any, category: str = "product"):
        """保存记忆"""
        path = self.base_dir / category / f"{key}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        logger.debug(f"Memory saved: {category}/{key}")

    async def load(self, key: str, category: str = "product") -> Optional[Any]:
        """加载记忆"""
        path = self.base_dir / category / f"{key}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except Exception:
            return None

    async def append_journal(self, entry: dict):
        """追加增长日志（学 Claude Code 的 Write-Ahead Log）"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        journal_dir = self.base_dir / "journal"
        path = journal_dir / f"{today}.jsonl"

        entry["timestamp"] = entry.get("timestamp", time.time())
        with open(path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    async def list_memories(self, category: str) -> list[str]:
        """列出某个类别的所有记忆"""
        cat_dir = self.base_dir / category
        if not cat_dir.exists():
            return []
        return [f.stem for f in cat_dir.glob("*.json")]

    async def search(self, query: str, categories: list[str] = None) -> list[dict]:
        """简单的关键词搜索记忆（后续可改为向量搜索）"""
        results = []
        for cat in (categories or self.CATEGORIES):
            cat_dir = self.base_dir / cat
            if not cat_dir.exists():
                continue
            for path in cat_dir.glob("*.json"):
                try:
                    content = path.read_text()
                    if query.lower() in content.lower():
                        results.append({
                            "category": cat,
                            "key": path.stem,
                            "preview": content[:200],
                        })
                except Exception:
                    continue
        return results
