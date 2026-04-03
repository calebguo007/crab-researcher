"""
CrabRes MCP Client — 调用外部 MCP 服务器

让 CrabRes Agent 能接入 MCP 生态：
- Brave Search MCP → 更好的搜索结果
- GitHub MCP → 分析用户的仓库
- SEMrush/Ahrefs MCP → 真实流量数据
- 任何用户配置的 MCP 服务器

MCP 协议核心：JSON-RPC 2.0 over HTTP
- tools/list → 获取可用工具列表
- tools/call → 调用某个工具

这是 OpenClaw/Claude Code 的核心能力之一。
"""

import json
import logging
from typing import Any, Optional
import httpx

from app.agent.tools import BaseTool, ToolDefinition

logger = logging.getLogger(__name__)


class MCPClient:
    """
    通用 MCP 客户端
    
    连接一个远程 MCP 服务器，发现它的工具，并能调用它们。
    """

    def __init__(self, server_url: str, name: str = "", api_key: str = ""):
        self.server_url = server_url.rstrip("/")
        self.name = name or server_url
        self.api_key = api_key
        self._tools_cache: Optional[list] = None

    async def list_tools(self) -> list[dict]:
        """发现远程 MCP 服务器的可用工具"""
        if self._tools_cache is not None:
            return self._tools_cache

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                resp = await client.post(
                    self.server_url,
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {},
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                tools = data.get("result", {}).get("tools", [])
                self._tools_cache = tools
                logger.info(f"MCP {self.name}: discovered {len(tools)} tools")
                return tools
        except Exception as e:
            logger.warning(f"MCP {self.name} tool discovery failed: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: dict = None) -> Any:
        """调用远程 MCP 工具"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                resp = await client.post(
                    self.server_url,
                    headers=headers,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": arguments or {},
                        },
                    },
                )
                resp.raise_for_status()
                data = resp.json()

                if "error" in data:
                    return {"error": data["error"].get("message", "Unknown MCP error")}

                result = data.get("result", {})
                # MCP 结果通常在 content 数组中
                content = result.get("content", [])
                if content and isinstance(content, list):
                    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    return {"result": "\n".join(texts)} if texts else {"result": json.dumps(content, ensure_ascii=False)}

                return {"result": json.dumps(result, ensure_ascii=False, default=str)}

        except httpx.TimeoutException:
            return {"error": f"MCP {self.name}/{tool_name} timed out"}
        except Exception as e:
            return {"error": f"MCP {self.name}/{tool_name} failed: {str(e)[:200]}"}


class MCPToolBridge(BaseTool):
    """
    将一个远程 MCP 工具桥接为 CrabRes 本地工具
    
    这样 Agent 可以像调用本地工具一样调用远程 MCP 工具。
    """

    def __init__(self, mcp_client: MCPClient, tool_spec: dict):
        self._client = mcp_client
        self._spec = tool_spec
        self._name = f"mcp_{mcp_client.name}_{tool_spec.get('name', 'unknown')}"

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self._name,
            description=f"[MCP: {self._client.name}] {self._spec.get('description', '')}",
            parameters=self._spec.get("inputSchema", {"type": "object", "properties": {}}),
            concurrent_safe=True,
        )

    async def execute(self, **kwargs) -> Any:
        return await self._client.call_tool(self._spec.get("name", ""), kwargs)


class MCPRegistry:
    """
    管理多个 MCP 服务器连接
    
    用户可以在配置中添加外部 MCP 服务器：
    MCP_SERVERS=brave:https://mcp.brave.com|github:https://mcp.github.com
    """

    def __init__(self):
        self._clients: dict[str, MCPClient] = {}

    def add_server(self, name: str, url: str, api_key: str = ""):
        self._clients[name] = MCPClient(server_url=url, name=name, api_key=api_key)
        logger.info(f"MCP Registry: added server '{name}' at {url}")

    async def discover_all_tools(self) -> list[MCPToolBridge]:
        """发现所有 MCP 服务器的工具，桥接为本地工具"""
        bridges = []
        for name, client in self._clients.items():
            tools = await client.list_tools()
            for tool_spec in tools:
                bridges.append(MCPToolBridge(client, tool_spec))
        logger.info(f"MCP Registry: {len(bridges)} tools discovered from {len(self._clients)} servers")
        return bridges

    def get_client(self, name: str) -> Optional[MCPClient]:
        return self._clients.get(name)

    @property
    def server_count(self) -> int:
        return len(self._clients)
