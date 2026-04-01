"""
CrabRes 专家 Agent 系统

12 位专家，每个都是一个带有专属 System Prompt + 工具集的子 Agent。
专家不直接面对用户，输出汇总到 Coordinator（首席增长官）。

设计原则（学 Claude Code Coordinator Mode）：
- 编排是 prompt 驱动的，不是硬编码流程
- "不要橡皮图章糟糕的工作"
- "必须理解发现后才能指派后续工作"
- 专家之间通过共享 context 沟通
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseExpert(ABC):
    """专家基类"""

    @property
    @abstractmethod
    def expert_id(self) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    async def analyze(self, context: dict, task: str) -> str:
        """执行分析任务，返回文字结果"""
        ...


class ExpertPool:
    """专家池"""

    def __init__(self):
        self._experts: dict[str, BaseExpert] = {}

    def register(self, expert: BaseExpert):
        self._experts[expert.expert_id] = expert

    def get(self, expert_id: str) -> BaseExpert | None:
        return self._experts.get(expert_id)

    def list_all(self) -> list[dict]:
        return [{"id": e.expert_id, "name": e.name} for e in self._experts.values()]
