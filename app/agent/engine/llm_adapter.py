"""
Agent LLM 适配器

把现有的 LLMService 包装成 Agent 引擎需要的接口。
支持：
- 普通对话（chat）
- 带工具调用的对话（chat with tools）
- 流式输出（streaming）

复用现有的多模型降级链和成本控制。
"""

import json
import logging
from typing import Any, Optional
from dataclasses import dataclass, field

from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    model: str = ""
    tokens_used: int = 0
    cost: float = 0.0


class AgentLLM:
    """
    Agent 专用 LLM 接口
    
    和 LLMService 的区别：
    - 不需要 db session（Agent 引擎自己管理成本追踪）
    - 支持 tool_use 格式
    - 支持 system prompt + messages 分离
    - 更轻量，专注于 Agent 的需要
    """

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._model = "moonshot-v1-128k"  # 默认模型
        self._base_url = "https://api.moonshot.cn/v1"
        self._api_key = settings.MOONSHOT_API_KEY
        self._total_tokens = 0
        self._total_cost = 0.0

        # 降级链
        self._fallback_configs = []
        if settings.DEEPSEEK_API_KEY:
            self._fallback_configs.append({
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
                "api_key": settings.DEEPSEEK_API_KEY,
            })
        if settings.OPENAI_API_KEY:
            self._fallback_configs.append({
                "model": "gpt-4o-mini",
                "base_url": None,
                "api_key": settings.OPENAI_API_KEY,
            })

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
        return self._client

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    @property
    def total_cost(self) -> float:
        return self._total_cost

    async def generate(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        生成响应
        
        Args:
            system_prompt: 系统提示（Coordinator/专家的 prompt）
            messages: 对话历史
            tools: 可用工具列表（OpenAI function calling 格式）
            temperature: 温度
            max_tokens: 最大 token
            
        Returns:
            LLMResponse: 包含 content 和/或 tool_calls
        """
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        # 构建请求参数
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # 如果有工具，转成 OpenAI function calling 格式
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                    },
                }
                for t in tools
            ]
            kwargs["tool_choice"] = "auto"

        try:
            response = await self.client.chat.completions.create(**kwargs)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"[AgentLLM] Primary model failed: {e}")
            return await self._fallback(full_messages, tools, temperature, max_tokens)

    def _parse_response(self, response) -> LLMResponse:
        """解析 OpenAI 格式响应"""
        choice = response.choices[0]
        usage = response.usage

        tokens = usage.total_tokens if usage else 0
        self._total_tokens += tokens

        result = LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used=tokens,
        )

        # 解析 tool calls
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}
                result.tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args": args,
                })

        return result

    async def _fallback(
        self,
        messages: list[dict],
        tools: list[dict] | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """降级到备选模型"""
        for config in self._fallback_configs:
            try:
                logger.info(f"[AgentLLM] Falling back to {config['model']}")
                client = AsyncOpenAI(
                    api_key=config["api_key"],
                    base_url=config.get("base_url"),
                )

                kwargs: dict[str, Any] = {
                    "model": config["model"],
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                if tools:
                    kwargs["tools"] = [
                        {
                            "type": "function",
                            "function": {
                                "name": t["name"],
                                "description": t.get("description", ""),
                                "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                            },
                        }
                        for t in tools
                    ]
                    kwargs["tool_choice"] = "auto"

                response = await client.chat.completions.create(**kwargs)
                result = self._parse_response(response)
                return result
            except Exception as e:
                logger.error(f"[AgentLLM] Fallback {config['model']} failed: {e}")
                continue

        # 所有模型都失败了
        return LLMResponse(
            content="[系统错误] 所有 LLM 模型均调用失败，请检查 API Key 配置。",
            model="error",
        )
