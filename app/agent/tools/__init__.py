"""
CrabRes 工具注册表

设计原则（学自 Claude Code）：
- 专用优于通用（search_reddit 而非 bash curl）
- 工具描述是 micro-prompt，直接影响 Agent 何时使用它
- 并发安全的工具标记为 concurrent_safe
- 工具结果有 budget 限制，超长结果写磁盘+只返回摘要
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict
    concurrent_safe: bool = True   # 是否可并行执行
    requires_auth: bool = False     # 是否需要用户授权
    result_budget: int = 20_000     # 结果最大字符数


class BaseTool(ABC):
    """所有工具的基类"""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """工具定义（名称、描述、参数 schema）"""
        ...

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行工具"""
        ...

    def truncate_result(self, result: str) -> str:
        """截断超长结果"""
        budget = self.definition.result_budget
        if len(result) <= budget:
            return result
        return result[:budget] + f"\n\n[结果已截断，完整结果共 {len(result)} 字符]"


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.definition.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_definitions(self) -> list[ToolDefinition]:
        return [t.definition for t in self._tools.values()]

    def get_concurrent_safe(self) -> list[str]:
        return [name for name, t in self._tools.items() if t.definition.concurrent_safe]
