import json
from typing import AsyncGenerator
import httpx
from models.messages import AgentConfig
from config import settings


class LLMProxy:
    """Unified interface for OpenAI and Anthropic streaming LLM calls."""

    @staticmethod
    async def stream_response(
        agent: AgentConfig,
        conversation_history: list[dict],
        system_prompt: str,
        token_limit: int | None = None,
    ) -> AsyncGenerator[str, None]:
        limit = token_limit or settings.default_token_limit
        api_base = agent.api_base.rstrip("/")

        if "anthropic" in api_base or "claude" in agent.model.lower():
            async for token in LLMProxy._call_anthropic(agent, conversation_history, system_prompt, limit):
                yield token
        else:
            async for token in LLMProxy._call_openai(agent, api_base, conversation_history, system_prompt, limit):
                yield token

    @staticmethod
    async def _call_openai(
        agent: AgentConfig,
        api_base: str,
        conversation_history: list[dict],
        system_prompt: str,
        token_limit: int,
    ) -> AsyncGenerator[str, None]:
        messages = [{"role": "system", "content": system_prompt}]

        for entry in conversation_history[-20:]:
            messages.append({
                "role": "assistant",
                "content": f"[{entry['agent_name']}]: {entry['content']}",
            })

        token_count = 0

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {agent.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": agent.model,
                    "messages": messages,
                    "stream": True,
                    "max_tokens": min(token_limit, 300),
                },
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(f"LLM API error {response.status_code}: {body.decode()}")

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        return
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            token_count += 1
                            if token_count > token_limit:
                                return
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    @staticmethod
    async def _call_anthropic(
        agent: AgentConfig,
        conversation_history: list[dict],
        system_prompt: str,
        token_limit: int,
    ) -> AsyncGenerator[str, None]:
        messages = []
        for entry in conversation_history[-20:]:
            messages.append({
                "role": "user",
                "content": f"[{entry['agent_name']}]: {entry['content']}",
            })
        messages.append({
            "role": "user",
            "content": "请基于以上对话历史发表你的观点。",
        })

        token_count = 0

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": agent.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": agent.model,
                    "system": system_prompt,
                    "messages": messages,
                    "max_tokens": min(token_limit, 300),
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise Exception(f"Anthropic API error {response.status_code}: {body.decode()}")

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    try:
                        data = json.loads(data_str)
                        if data.get("type") == "content_block_delta":
                            content = data.get("delta", {}).get("text", "")
                            if content:
                                token_count += 1
                                if token_count > token_limit:
                                    return
                                yield content
                    except (json.JSONDecodeError, KeyError):
                        continue


llm_proxy = LLMProxy()
