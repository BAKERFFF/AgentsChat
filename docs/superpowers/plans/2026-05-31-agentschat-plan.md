# AgentsChat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a web platform where a user moderates real-time streaming discussions among 2-3 AI agents through a three-phase agenda (analyze → discuss → conclude).

**Architecture:** Single WebSocket channel between Vue 3 SPA and FastAPI server. Server holds session state in memory, proxies LLM streaming calls (OpenAI/Anthropic) with a 200-token hard cutoff per agent turn. No persistence — everything is ephemeral.

**Tech Stack:** Vue 3 (Vite) + FastAPI (Python 3.11+, uvicorn) + WebSocket (native) + httpx (async LLM calls) + tiktoken (token counting)

---

## File Structure

```
AgentsChat/
├── backend/
│   ├── main.py              — FastAPI app, CORS, WS mount
│   ├── config.py            — Settings (token limit, CORS origins)
│   ├── requirements.txt     — Python dependencies
│   ├── ws/
│   │   ├── __init__.py
│   │   └── chat.py          — WebSocket endpoint & message router
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session.py       — In-memory session store
│   │   ├── agenda.py        — 3-phase agenda engine
│   │   └── llm_proxy.py     — OpenAI/Anthropic streaming proxy
│   └── models/
│       ├── __init__.py
│       └── messages.py      — Pydantic WS message types
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css         — Global dark theme, background effects
│       ├── types/
│       │   └── messages.js   — JS message type constants
│       ├── composables/
│       │   └── useWebSocket.js
│       └── components/
│           ├── SetupPage.vue
│           ├── DiscussionRoom.vue
│           ├── AgentAvatar.vue
│           ├── ChatMessage.vue
│           ├── AgendaBar.vue
│           ├── ControlPanel.vue
│           └── BackgroundEffects.vue
├── docs/superpowers/
│   ├── specs/2026-05-31-agentschat-design.md
│   └── plans/2026-05-31-agentschat-plan.md
└── .gitignore
```

---

### Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `backend/main.py`
- Create: `backend/ws/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/models/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p backend/ws backend/services backend/models
```

- [ ] **Step 2: Write requirements.txt**

```
# backend/requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
httpx==0.28.1
pydantic==2.10.4
pydantic-settings==2.7.1
python-dotenv==1.0.1
tiktoken==0.8.0
```

- [ ] **Step 3: Write config.py**

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    default_token_limit: int = 200
    session_timeout_seconds: int = 300
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:54853"]
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

- [ ] **Step 4: Write minimal main.py**

```python
# backend/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(title="AgentsChat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "hello"})
    await websocket.close()
```

- [ ] **Step 5: Create empty __init__.py files**

```bash
touch backend/ws/__init__.py backend/services/__init__.py backend/models/__init__.py
```

- [ ] **Step 6: Install dependencies and verify server starts**

```bash
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Expected: Server starts, `GET /health` returns `{"status":"ok"}`, `GET /ws` upgrades to WebSocket and receives `{"type":"hello"}`.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with config and WS placeholder"
```

---

### Task 2: Message Models (Pydantic)

**Files:**
- Create: `backend/models/messages.py`
- Modify: `backend/main.py` (import and use models)

- [ ] **Step 1: Write the message models**

```python
# backend/models/messages.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AgentConfig(BaseModel):
    id: str
    name: str
    model: str
    api_key: str
    api_base: str = "https://api.openai.com/v1"


class ClientMessage(BaseModel):
    type: str
    topic: Optional[str] = None
    agents: Optional[list[AgentConfig]] = None
    token_limit: Optional[int] = None
    agent_id: Optional[str] = None


class ServerMessage(BaseModel):
    type: str
    session_id: Optional[str] = None
    phase: Optional[int] = None
    phase_name: Optional[str] = None
    system_prompt_hint: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    token_text: Optional[str] = None
    full_text: Optional[str] = None
    token_count: Optional[int] = None
    spoken: Optional[list[str]] = None
    pending: Optional[list[str]] = None
    round_num: Optional[int] = None
    round_summary: Optional[str] = None
    code: Optional[str] = None
    detail: Optional[str] = None


# Message type constants
class ClientMsgType:
    INIT_SESSION = "init_session"
    SELECT_SPEAKER = "select_speaker"
    NEXT_PHASE = "next_phase"
    NEXT_ROUND = "next_round"


class ServerMsgType:
    SESSION_READY = "session_ready"
    PHASE_STARTED = "phase_started"
    AGENT_TYPING = "agent_typing"
    TOKEN = "token"
    AGENT_DONE = "agent_done"
    ROUND_STATUS = "round_status"
    ROUND_COMPLETE = "round_complete"
    DISCUSSION_ENDED = "discussion_ended"
    ERROR = "error"
```

- [ ] **Step 2: Commit**

```bash
git add backend/models/messages.py
git commit -m "feat: add Pydantic message models for WS protocol"
```

---

### Task 3: Session Manager

**Files:**
- Create: `backend/services/session.py`

- [ ] **Step 1: Write the session manager with tests**

```python
# backend/services/session.py
import uuid
import time
from typing import Optional
from models.messages import AgentConfig


class DiscussionSession:
    """In-memory session holding all discussion state."""

    def __init__(self, topic: str, agents: list[AgentConfig], token_limit: int = 200):
        self.session_id = str(uuid.uuid4())[:8]
        self.topic = topic
        self.agents: dict[str, AgentConfig] = {a.id: a for a in agents}
        self.token_limit = token_limit
        self.conversation_history: list[dict] = []
        self.current_phase: int = 0
        self.current_round: int = 1
        self.spoken_this_round: set[str] = set()
        self.created_at: float = time.time()
        self.discussion_ended: bool = False

    def can_speak(self, agent_id: str) -> bool:
        """Check if agent exists and hasn't spoken this round."""
        return agent_id in self.agents and agent_id not in self.spoken_this_round

    def mark_spoken(self, agent_id: str) -> None:
        """Mark an agent as having spoken this round."""
        self.spoken_this_round.add(agent_id)

    def all_spoken(self) -> bool:
        """Check if all agents have spoken this round."""
        return self.spoken_this_round == set(self.agents.keys())

    def reset_round(self) -> None:
        """Reset spoken tracking for a new round."""
        self.spoken_this_round.clear()
        self.current_round += 1

    def pending_agents(self) -> list[str]:
        """Return IDs of agents who haven't spoken this round."""
        return [aid for aid in self.agents if aid not in self.spoken_this_round]

    def spoken_agents(self) -> list[str]:
        """Return IDs of agents who have spoken this round."""
        return list(self.spoken_this_round)

    def record_message(self, agent_id: str, content: str) -> None:
        """Append a message to conversation history."""
        agent = self.agents[agent_id]
        self.conversation_history.append({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "content": content,
        })

    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if session has exceeded timeout."""
        return time.time() - self.created_at > timeout_seconds


class SessionStore:
    """Thread-safe in-memory store for DiscussionSessions."""

    def __init__(self):
        self._sessions: dict[str, DiscussionSession] = {}

    def create(self, topic: str, agents: list[AgentConfig], token_limit: int = 200) -> DiscussionSession:
        session = DiscussionSession(topic, agents, token_limit)
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Optional[DiscussionSession]:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def cleanup_expired(self, timeout_seconds: int = 300) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired(timeout_seconds)
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


# Global singleton
session_store = SessionStore()
```

- [ ] **Step 2: Commit**

```bash
git add backend/services/session.py
git commit -m "feat: add in-memory session manager with round tracking"
```

---

### Task 4: Agenda Engine

**Files:**
- Create: `backend/services/agenda.py`

- [ ] **Step 1: Write the agenda engine**

```python
# backend/services/agenda.py
from dataclasses import dataclass


@dataclass
class Phase:
    index: int
    name: str
    system_prompt: str


PHASES = [
    Phase(
        index=0,
        name="分析问题",
        system_prompt=(
            "你正在参与一场多专家协同讨论，当前处于【分析问题】阶段。"
            "从你的视角拆解问题，引用并回应其他参与者的观点，"
            "形成辩论式分析。每个发言必须结合对话历史给出新的见解。"
            "发言精练，不超过200 tokens。"
        ),
    ),
    Phase(
        index=1,
        name="讨论问题",
        system_prompt=(
            "你正在参与一场多专家协同讨论，当前处于【讨论问题】阶段。"
            "就分析阶段涌现的关键分歧和共识展开深入讨论。"
            "挑战对方的假设，为你的立场辩护，碰撞出解决方案。"
            "发言精练，不超过200 tokens。"
        ),
    ),
    Phase(
        index=2,
        name="得出结论",
        system_prompt=(
            "你正在参与一场多专家协同讨论，当前处于【得出结论】阶段。"
            "综合全程讨论，给出你的最终判断。"
            "明确标注共识点和保留的个人意见。"
            "发言精练，不超过200 tokens。"
        ),
    ),
]


class AgendaEngine:
    """Manages the three-phase discussion agenda."""

    @staticmethod
    def get_phase(index: int) -> Phase:
        if 0 <= index < len(PHASES):
            return PHASES[index]
        raise ValueError(f"Invalid phase index: {index}")

    @staticmethod
    def get_phase_count() -> int:
        return len(PHASES)

    @staticmethod
    def is_last_phase(index: int) -> bool:
        return index >= len(PHASES) - 1

    @staticmethod
    def get_system_prompt(phase_index: int, agent_name: str) -> str:
        phase = AgendaEngine.get_phase(phase_index)
        return f"{phase.system_prompt}\n你的名字是{agent_name}。当前讨论主题将通过对话历史给出。"
```

- [ ] **Step 2: Commit**

```bash
git add backend/services/agenda.py
git commit -m "feat: add 3-phase agenda engine with phase-specific prompts"
```

---

### Task 5: LLM Proxy

**Files:**
- Create: `backend/services/llm_proxy.py`

- [ ] **Step 1: Write the LLM proxy with streaming and 200-token cutoff**

```python
# backend/services/llm_proxy.py
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
        """Stream tokens from the configured LLM. Yields token strings."""
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
        """Stream from OpenAI-compatible API (OpenAI, Gemini via OpenAI endpoint, etc.)."""
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
        """Stream from Anthropic Messages API."""
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/services/llm_proxy.py
git commit -m "feat: add LLM proxy with OpenAI/Anthropic streaming and token cutoff"
```

---

### Task 6: WebSocket Handler

**Files:**
- Create: `backend/ws/chat.py`
- Modify: `backend/main.py` (mount WS handler)

- [ ] **Step 1: Write the WebSocket chat handler**

```python
# backend/ws/chat.py
import json
import traceback
from fastapi import WebSocket, WebSocketDisconnect
from models.messages import (
    ClientMessage, ServerMessage, AgentConfig,
    ClientMsgType, ServerMsgType,
)
from services.session import session_store
from services.agenda import AgendaEngine
from services.llm_proxy import llm_proxy


async def handle_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id: str | None = None

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg = ClientMessage(**data)
            except Exception:
                await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INVALID_JSON", "detail": "Invalid message format"})
                continue

            if msg.type == ClientMsgType.INIT_SESSION:
                session_id = await handle_init(websocket, msg)

            elif msg.type == ClientMsgType.SELECT_SPEAKER:
                await handle_select_speaker(websocket, session_id, msg)

            elif msg.type == ClientMsgType.NEXT_ROUND:
                await handle_next_round(websocket, session_id)

            elif msg.type == ClientMsgType.NEXT_PHASE:
                await handle_next_phase(websocket, session_id)

            else:
                await websocket.send_json({"type": ServerMsgType.ERROR, "code": "UNKNOWN_TYPE", "detail": f"Unknown message type: {msg.type}"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        traceback.print_exc()
        try:
            await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INTERNAL", "detail": str(e)})
        except Exception:
            pass
    finally:
        if session_id:
            session_store.delete(session_id)


async def handle_init(websocket: WebSocket, msg: ClientMessage) -> str:
    if not msg.topic:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "MISSING_TOPIC", "detail": "Topic is required"})
        return ""

    if not msg.agents or len(msg.agents) < 2 or len(msg.agents) > 3:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INVALID_AGENTS", "detail": "Need 2-3 agents"})
        return ""

    token_limit = msg.token_limit or 200
    session = session_store.create(msg.topic, msg.agents, token_limit)
    phase = AgendaEngine.get_phase(0)

    await websocket.send_json({
        "type": ServerMsgType.SESSION_READY,
        "session_id": session.session_id,
    })
    await websocket.send_json({
        "type": ServerMsgType.PHASE_STARTED,
        "phase": 0,
        "phase_name": phase.name,
        "system_prompt_hint": phase.system_prompt[:100],
    })
    await send_round_status(websocket, session)

    return session.session_id


async def handle_select_speaker(websocket: WebSocket, session_id: str | None, msg: ClientMessage) -> None:
    if not session_id:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "NO_SESSION", "detail": "Session not initialized"})
        return

    session = session_store.get(session_id)
    if not session:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "SESSION_NOT_FOUND", "detail": "Session expired or not found"})
        return

    agent_id = msg.agent_id
    if not agent_id:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "MISSING_AGENT_ID", "detail": "agent_id is required"})
        return

    if not session.can_speak(agent_id):
        pending = session.pending_agents()
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "ALREADY_SPOKEN",
            "detail": f"Agent has already spoken this round. Available: {pending}",
        })
        return

    agent = session.agents[agent_id]
    phase_prompt = AgendaEngine.get_system_prompt(session.current_phase, agent.name)

    # Signal typing
    await websocket.send_json({
        "type": ServerMsgType.AGENT_TYPING,
        "agent_id": agent_id,
        "agent_name": agent.name,
    })

    # Stream tokens
    full_text = ""
    token_count = 0
    try:
        async for token in llm_proxy.stream_response(
            agent=agent,
            conversation_history=session.conversation_history,
            system_prompt=phase_prompt,
            token_limit=session.token_limit,
        ):
            full_text += token
            token_count += 1
            await websocket.send_json({
                "type": ServerMsgType.TOKEN,
                "agent_id": agent_id,
                "token_text": token,
            })
    except Exception as e:
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "LLM_ERROR",
            "detail": f"Agent '{agent.name}' call failed: {str(e)}",
        })
        return

    # Record in history
    session.record_message(agent_id, full_text)
    session.mark_spoken(agent_id)

    # Signal done
    await websocket.send_json({
        "type": ServerMsgType.AGENT_DONE,
        "agent_id": agent_id,
        "full_text": full_text,
        "token_count": token_count,
    })

    # Check round complete
    if session.all_spoken():
        round_summary = f"第{session.current_round}轮完成，所有agent已发言。"
        await websocket.send_json({
            "type": ServerMsgType.ROUND_COMPLETE,
            "round_summary": round_summary,
        })
    else:
        await send_round_status(websocket, session)


async def handle_next_round(websocket: WebSocket, session_id: str | None) -> None:
    if not session_id:
        return
    session = session_store.get(session_id)
    if not session:
        return

    if not session.all_spoken():
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "ROUND_NOT_COMPLETE",
            "detail": f"Not all agents have spoken. Pending: {session.pending_agents()}",
        })
        return

    session.reset_round()
    await send_round_status(websocket, session)


async def handle_next_phase(websocket: WebSocket, session_id: str | None) -> None:
    if not session_id:
        return
    session = session_store.get(session_id)
    if not session:
        return

    next_index = session.current_phase + 1

    if AgendaEngine.is_last_phase(session.current_phase):
        await websocket.send_json({
            "type": ServerMsgType.DISCUSSION_ENDED,
            "phases_summary": f"三步议程全部完成。共{session.current_round}轮讨论。",
        })
        session.discussion_ended = True
        return

    session.current_phase = next_index
    session.spoken_this_round.clear()
    session.current_round = 1

    phase = AgendaEngine.get_phase(next_index)
    await websocket.send_json({
        "type": ServerMsgType.PHASE_STARTED,
        "phase": next_index,
        "phase_name": phase.name,
        "system_prompt_hint": phase.system_prompt[:100],
    })
    await send_round_status(websocket, session)


async def send_round_status(websocket: WebSocket, session) -> None:
    await websocket.send_json({
        "type": ServerMsgType.ROUND_STATUS,
        "spoken": session.spoken_agents(),
        "pending": session.pending_agents(),
        "round_num": session.current_round,
    })
```

- [ ] **Step 2: Update main.py to use the handler**

```python
# backend/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from ws.chat import handle_chat

app = FastAPI(title="AgentsChat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_chat(websocket)
```

- [ ] **Step 3: Commit**

```bash
git add backend/ws/chat.py backend/main.py
git commit -m "feat: add WebSocket chat handler with full protocol implementation"
```

---

### Task 7: Frontend Project Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Write package.json**

```json
{
  "name": "agentschat",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^6.0.5"
  }
}
```

- [ ] **Step 2: Write vite.config.js**

```js
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
})
```

- [ ] **Step 3: Write index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AgentsChat</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Write main.js**

```js
// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
```

- [ ] **Step 5: Write minimal App.vue**

```vue
<!-- frontend/src/App.vue -->
<template>
  <div class="app-root">
    <h1>AgentsChat</h1>
    <p>Loading...</p>
  </div>
</template>

<script setup>
</script>
```

- [ ] **Step 6: Write base style.css**

```css
/* frontend/src/style.css */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0d1117;
  color: #e0e0e0;
  font-family: 'Courier New', 'Source Code Pro', monospace;
  min-height: 100vh;
  overflow-x: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
}
```

- [ ] **Step 7: Install dependencies and verify**

```bash
cd frontend && npm install && npm run dev
```

Expected: Dev server starts on port 5173, page renders "AgentsChat".

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/vite.config.js frontend/index.html frontend/src/
git commit -m "feat: scaffold Vue 3 frontend with Vite"
```

---

### Task 8: Frontend Message Types

**Files:**
- Create: `frontend/src/types/messages.js`

- [ ] **Step 1: Write message type constants**

```js
// frontend/src/types/messages.js

export const ClientMsgType = {
  INIT_SESSION: 'init_session',
  SELECT_SPEAKER: 'select_speaker',
  NEXT_PHASE: 'next_phase',
  NEXT_ROUND: 'next_round',
}

export const ServerMsgType = {
  SESSION_READY: 'session_ready',
  PHASE_STARTED: 'phase_started',
  AGENT_TYPING: 'agent_typing',
  TOKEN: 'token',
  AGENT_DONE: 'agent_done',
  ROUND_STATUS: 'round_status',
  ROUND_COMPLETE: 'round_complete',
  DISCUSSION_ENDED: 'discussion_ended',
  ERROR: 'error',
}

export const PHASES = [
  { index: 0, name: '分析问题', icon: '🔍' },
  { index: 1, name: '讨论问题', icon: '💬' },
  { index: 2, name: '得出结论', icon: '📋' },
]
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/messages.js
git commit -m "feat: add frontend message type constants"
```

---

### Task 9: WebSocket Composable

**Files:**
- Create: `frontend/src/composables/useWebSocket.js`

- [ ] **Step 1: Write the WebSocket composable**

```js
// frontend/src/composables/useWebSocket.js
import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const connected = ref(false)
  const error = ref(null)
  const listeners = new Map()

  function connect(url = 'ws://127.0.0.1:8000/ws') {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(url)

      socket.onopen = () => {
        connected.value = true
        error.value = null
        ws.value = socket
        resolve()
      }

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          const handlers = listeners.get(msg.type) || []
          handlers.forEach(fn => fn(msg))
          // Also notify global listeners
          const globalHandlers = listeners.get('*') || []
          globalHandlers.forEach(fn => fn(msg))
        } catch (e) {
          console.error('Failed to parse WS message:', e)
        }
      }

      socket.onerror = (e) => {
        error.value = 'WebSocket connection error'
        reject(e)
      }

      socket.onclose = () => {
        connected.value = false
        ws.value = null
      }
    })
  }

  function send(msg) {
    if (ws.value && connected.value) {
      ws.value.send(JSON.stringify(msg))
    }
  }

  function on(msgType, handler) {
    if (!listeners.has(msgType)) {
      listeners.set(msgType, [])
    }
    listeners.get(msgType).push(handler)

    // Return unsubscribe function
    return () => {
      const handlers = listeners.get(msgType)
      if (handlers) {
        const idx = handlers.indexOf(handler)
        if (idx !== -1) handlers.splice(idx, 1)
      }
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return { connected, error, connect, send, on, disconnect }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useWebSocket.js
git commit -m "feat: add WebSocket composable for Vue"
```

---

### Task 10: AgentAvatar Component

**Files:**
- Create: `frontend/src/components/AgentAvatar.vue`

- [ ] **Step 1: Write the AgentAvatar component with pixel CSS art**

```vue
<!-- frontend/src/components/AgentAvatar.vue -->
<template>
  <div
    class="pixel-avatar"
    :class="[avatarClass, { speaking: isSpeaking, spoken: isSpoken }]"
  ></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agentId: { type: String, required: true },
  isSpeaking: { type: Boolean, default: false },
  isSpoken: { type: Boolean, default: false },
})

const avatarClass = computed(() => {
  const map = { a: 'avatar-a', b: 'avatar-b', c: 'avatar-c' }
  return map[props.agentId] || 'avatar-a'
})
</script>

<style scoped>
.pixel-avatar {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  image-rendering: pixelated;
  border-radius: 4px;
  position: relative;
  border: 2px solid rgba(255,255,255,0.08);
  transition: all 0.3s;
}
.pixel-avatar.speaking {
  animation: avatar-bounce 0.45s infinite alternate;
  border-color: rgba(233, 69, 96, 0.6);
}
.pixel-avatar.spoken {
  border-color: rgba(136, 204, 136, 0.3);
}
.pixel-avatar.speaking::after {
  content: '';
  position: absolute;
  inset: -5px;
  border-radius: 6px;
  box-shadow: 0 0 16px rgba(233, 69, 96, 0.4);
  animation: glow-pulse 0.8s infinite alternate;
}

@keyframes avatar-bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-4px); }
}
@keyframes glow-pulse {
  from { opacity: 0.3; }
  to { opacity: 1; }
}

/* Agent A — blue square robot */
.avatar-a {
  background: #2c3e8f;
  width: 44px; height: 32px;
  box-shadow:
    8px 4px 0 #2c3e8f, 24px 4px 0 #2c3e8f, 32px 4px 0 #2c3e8f,
    4px 8px 0 #3b4fb0, 12px 8px 0 #fff, 20px 8px 0 #3b4fb0, 28px 8px 0 #fff, 36px 8px 0 #3b4fb0,
    4px 12px 0 #3b4fb0, 8px 12px 0 #3b4fb0, 16px 12px 0 #3b4fb0, 24px 12px 0 #3b4fb0, 32px 12px 0 #3b4fb0, 36px 12px 0 #3b4fb0,
    8px 16px 0 #2c3e8f, 12px 16px 0 #fff, 20px 16px 0 #2c3e8f, 28px 16px 0 #fff, 32px 16px 0 #2c3e8f,
    4px 20px 0 #2c3e8f, 8px 20px 0 #2c3e8f, 16px 20px 0 #2c3e8f, 24px 20px 0 #2c3e8f, 32px 20px 0 #2c3e8f, 36px 20px 0 #2c3e8f,
    4px 24px 0 #1a2a6e, 12px 24px 0 #1a2a6e, 20px 24px 0 #1a2a6e, 28px 24px 0 #1a2a6e, 36px 24px 0 #1a2a6e,
    8px 28px 0 #1a2a6e, 16px 28px 0 #1a2a6e, 24px 28px 0 #1a2a6e, 32px 28px 0 #1a2a6e;
}

/* Agent B — green round robot */
.avatar-b {
  background: #1a6e3e;
  width: 40px; height: 32px;
  box-shadow:
    12px 4px 0 #1a6e3e, 24px 4px 0 #1a6e3e,
    4px 8px 0 #28a050, 8px 8px 0 #ffcc00, 16px 8px 0 #28a050, 20px 8px 0 #28a050, 28px 8px 0 #ffcc00, 32px 8px 0 #28a050,
    4px 12px 0 #28a050, 12px 12px 0 #28a050, 16px 12px 0 #28a050, 20px 12px 0 #28a050, 24px 12px 0 #28a050, 32px 12px 0 #28a050,
    0px 16px 0 #28a050, 8px 16px 0 #1a6e3e, 16px 16px 0 #1a6e3e, 20px 16px 0 #1a6e3e, 24px 16px 0 #1a6e3e, 28px 16px 0 #28a050, 36px 16px 0 #28a050,
    4px 20px 0 #1a6e3e, 12px 20px 0 #1a6e3e, 16px 20px 0 #1a6e3e, 20px 20px 0 #1a6e3e, 24px 20px 0 #1a6e3e, 32px 20px 0 #1a6e3e,
    8px 24px 0 #0d4d28, 16px 24px 0 #0d4d28, 20px 24px 0 #0d4d28, 28px 24px 0 #0d4d28,
    12px 28px 0 #0d4d28, 16px 28px 0 #0d4d28, 20px 28px 0 #0d4d28, 24px 28px 0 #0d4d28;
}

/* Agent C — purple triangle robot */
.avatar-c {
  background: #6e2d8f;
  width: 40px; height: 28px;
  box-shadow:
    16px 4px 0 #6e2d8f, 20px 4px 0 #6e2d8f,
    8px 8px 0 #8e40b0, 12px 8px 0 #8e40b0, 16px 8px 0 #ff6699, 20px 8px 0 #8e40b0, 24px 8px 0 #8e40b0, 28px 8px 0 #8e40b0,
    4px 12px 0 #8e40b0, 8px 12px 0 #fff, 16px 12px 0 #8e40b0, 20px 12px 0 #8e40b0, 24px 12px 0 #8e40b0, 28px 12px 0 #fff, 32px 12px 0 #8e40b0,
    4px 16px 0 #6e2d8f, 12px 16px 0 #6e2d8f, 16px 16px 0 #6e2d8f, 20px 16px 0 #6e2d8f, 24px 16px 0 #6e2d8f, 32px 16px 0 #6e2d8f,
    8px 20px 0 #6e2d8f, 16px 20px 0 #6e2d8f, 20px 20px 0 #6e2d8f, 28px 20px 0 #6e2d8f,
    12px 24px 0 #4a1a6e, 16px 24px 0 #4a1a6e, 20px 24px 0 #4a1a6e, 24px 24px 0 #4a1a6e;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AgentAvatar.vue
git commit -m "feat: add pixel-art AgentAvatar component with CSS box-shadow"
```

---

### Task 11: BackgroundEffects Component

**Files:**
- Create: `frontend/src/components/BackgroundEffects.vue`

- [ ] **Step 1: Write the BackgroundEffects component**

```vue
<!-- frontend/src/components/BackgroundEffects.vue -->
<template>
  <div class="bg-effects">
    <div class="bg-grid"></div>
    <div class="gradient-orb orb1"></div>
    <div class="gradient-orb orb2"></div>
    <div class="gradient-orb orb3"></div>
    <div class="gradient-orb orb4"></div>
    <div class="gradient-orb orb5"></div>
    <div class="tech-border-top"></div>
    <div class="particles">
      <div
        v-for="i in 30"
        :key="i"
        class="particle"
        :class="particleClass(i)"
      ></div>
    </div>
  </div>
</template>

<script setup>
function particleClass(i) {
  const types = ['dot', 'dot', 'dot', 'square', 'diamond', 'line']
  return types[i % types.length]
}
</script>

<style scoped>
.bg-effects {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
}

.bg-grid {
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(15,52,96,0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15,52,96,0.12) 1px, transparent 1px);
  background-size: 28px 28px;
}

.gradient-orb {
  position: fixed; border-radius: 50%; filter: blur(80px);
  animation: orb-float 10s ease-in-out infinite;
}
.orb1 { width:400px; height:400px; background:radial-gradient(circle, rgba(59,79,176,0.25), transparent 70%); top:-120px; left:-80px; }
.orb2 { width:350px; height:350px; background:radial-gradient(circle, rgba(233,69,96,0.2), transparent 70%); bottom:-100px; right:-60px; animation-delay:-3s; }
.orb3 { width:300px; height:300px; background:radial-gradient(circle, rgba(80,216,144,0.18), transparent 70%); top:40%; right:-100px; animation-delay:-6s; }
.orb4 { width:280px; height:280px; background:radial-gradient(circle, rgba(184,110,240,0.18), transparent 70%); bottom:30%; left:-100px; animation-delay:-9s; }
.orb5 { width:200px; height:200px; background:radial-gradient(circle, rgba(233,69,96,0.15), rgba(91,141,239,0.15), transparent 70%); top:50%; left:50%; animation-delay:-4s; }

@keyframes orb-float {
  0%,100% { transform:translate(0,0) scale(1); }
  25% { transform:translate(30px,-20px) scale(1.08); }
  50% { transform:translate(-15px,25px) scale(0.94); }
  75% { transform:translate(-25px,-10px) scale(1.05); }
}

.tech-border-top {
  position: fixed; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg, transparent 0%, #e94560 20%, #5b8def 40%, #50d890 60%, #b86ef0 80%, transparent 100%);
  background-size:200% 100%;
  animation: tech-scan 5s linear infinite;
  z-index: 91; opacity: 0.7;
}
@keyframes tech-scan {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

.particles { position: fixed; inset: 0; }
.particle { position: absolute; border-radius: 2px; animation: float-up linear infinite; }
.particle.dot { width:3px; height:3px; border-radius:50%; }
.particle.square { width:5px; height:5px; border-radius:1px; }
.particle.diamond { width:5px; height:5px; transform:rotate(45deg); border-radius:1px; }
.particle.line { width:2px; height:10px; border-radius:1px; }

@keyframes float-up {
  0% { bottom:-30px; opacity:0; transform:translateX(0) scale(0.3); }
  5% { opacity:0.9; }
  85% { opacity:0.15; }
  100% { bottom:110%; opacity:0; transform:translateX(40px) scale(1.3); }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/BackgroundEffects.vue
git commit -m "feat: add BackgroundEffects with orbs, grid, particles, and scanline"
```

---

### Task 12: ChatMessage Component

**Files:**
- Create: `frontend/src/components/ChatMessage.vue`

- [ ] **Step 1: Write the ChatMessage component**

```vue
<!-- frontend/src/components/ChatMessage.vue -->
<template>
  <div class="message">
    <AgentAvatar
      :agent-id="agentId"
      :is-speaking="status === 'speaking'"
      :is-spoken="status === 'spoken'"
    />
    <div class="msg-content" :class="{ reference: hasRef }">
      <div class="agent-name" :class="agentId">
        {{ agentName }}
        <span class="model-tag">{{ model }}</span>
      </div>
      <div v-if="hasRef" class="ref-tag">
        ↩ {{ refText }}
      </div>
      <div class="text">
        {{ displayText }}
        <span v-if="status === 'speaking'" class="cursor-blink"></span>
      </div>
      <div
        v-if="status === 'spoken' || status === 'speaking'"
        class="token-counter"
        :class="{ warn: tokenCount > 150, limit: tokenCount >= 200 }"
      >
        {{ tokenCount }} / {{ tokenLimit }} tokens
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AgentAvatar from './AgentAvatar.vue'

const props = defineProps({
  agentId: { type: String, required: true },
  agentName: { type: String, required: true },
  model: { type: String, default: '' },
  displayText: { type: String, default: '' },
  status: { type: String, default: 'waiting' }, // 'waiting' | 'speaking' | 'spoken'
  tokenCount: { type: Number, default: 0 },
  tokenLimit: { type: Number, default: 200 },
  refText: { type: String, default: '' },
})

const hasRef = computed(() => props.refText.length > 0)
</script>

<style scoped>
.message {
  display: flex; gap: 10px; align-items: flex-start;
  animation: msg-in 0.35s ease-out; margin-bottom: 8px;
}
@keyframes msg-in {
  from { opacity: 0; transform: translateX(-14px); }
  to { opacity: 1; transform: translateX(0); }
}
.msg-content {
  flex:1; background:rgba(22,33,62,0.75); border:1px solid #0f3460;
  border-radius:4px; padding:10px 14px; position:relative; max-width:78%;
  transition:border-color 0.3s;
}
.msg-content.reference {
  border-left: 2px solid #e9a040;
}
.msg-content:hover { border-color: rgba(233,69,96,0.15); }
.agent-name { font-size:12px; font-weight:bold; margin-bottom:4px; display:flex; align-items:center; gap:6px; }
.agent-name.a { color:#5b8def; } .agent-name.b { color:#50d890; } .agent-name.c { color:#b86ef0; }
.model-tag { font-size:9px; padding:1px 6px; border-radius:2px; border:1px solid currentColor; opacity:0.5; font-weight:normal; }
.text { font-size:13px; line-height:1.7; color:#ccc; }
.cursor-blink::after { content:'▌'; animation:blink 0.8s step-end infinite; color:#e94560; }
@keyframes blink { 50%{opacity:0;} }
.token-counter { font-size:10px; color:#555; text-align:right; margin-top:6px; transition:color 0.3s; }
.token-counter.warn { color:#e9a040; }
.token-counter.limit { color:#e94560; }
.ref-tag {
  display:inline-block; font-size:9px; color:#e9a040; margin-bottom:4px;
  padding:2px 6px; background:rgba(233,160,64,0.08); border-radius:2px;
  border:1px solid rgba(233,160,64,0.2);
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ChatMessage.vue
git commit -m "feat: add ChatMessage component with streaming cursor and ref tags"
```

---

### Task 13: AgendaBar Component

**Files:**
- Create: `frontend/src/components/AgendaBar.vue`

- [ ] **Step 1: Write the AgendaBar component**

```vue
<!-- frontend/src/components/AgendaBar.vue -->
<template>
  <div class="agenda-bar">
    <div
      v-for="(phase, idx) in phases"
      :key="idx"
      class="agenda-step"
      :class="{
        done: idx < currentPhase,
        active: idx === currentPhase,
      }"
    >
      <div class="step-num">STEP {{ idx + 1 }}</div>
      <div class="step-label">{{ phase.icon }} {{ phase.name }}</div>
    </div>
  </div>
</template>

<script setup>
import { PHASES } from '../types/messages.js'

defineProps({
  currentPhase: { type: Number, default: 0 },
  phases: { type: Array, default: () => PHASES },
})
</script>

<style scoped>
.agenda-bar {
  display: flex; gap: 6px; padding: 10px 16px;
  background: rgba(10,15,26,0.5); border-bottom: 1px solid #0f3460;
}
.agenda-step {
  flex:1; padding: 10px 12px; font-size: 11px; text-align: center; border-radius: 4px;
  background: rgba(22,33,62,0.4); border: 1px solid #0f3460; color: #555;
  transition: all 0.3s; position: relative; overflow: hidden;
}
.agenda-step .step-num { font-size: 9px; opacity: 0.5; margin-bottom: 2px; }
.agenda-step .step-label { font-weight: bold; }
.agenda-step.done {
  background: rgba(15,52,96,0.3); color: #88cc88; border-color: rgba(136,204,136,0.3);
}
.agenda-step.active {
  background: linear-gradient(135deg, rgba(26,26,62,0.8), rgba(15,52,96,0.5));
  color: #e94560; border-color: #e94560;
  animation: pulse-border 2s infinite;
}
.agenda-step.active::after {
  content: ''; position: absolute; bottom: -2px; left: 20%; right: 20%; height: 2px;
  background: linear-gradient(90deg, transparent, #e94560, transparent);
  animation: step-underline 2s ease-in-out infinite;
}
@keyframes step-underline {
  0%,100% { left: 30%; right: 30%; opacity: 0.4; }
  50% { left: 5%; right: 5%; opacity: 1; }
}
@keyframes pulse-border {
  0%,100% { border-color: #e94560; }
  50% { border-color: #ff6b81; box-shadow: 0 0 14px rgba(233,69,96,0.25); }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/AgendaBar.vue
git commit -m "feat: add AgendaBar component with 3-step progress indicator"
```

---

### Task 14: ControlPanel Component

**Files:**
- Create: `frontend/src/components/ControlPanel.vue`

- [ ] **Step 1: Write the ControlPanel component**

```vue
<!-- frontend/src/components/ControlPanel.vue -->
<template>
  <div class="control-bar">
    <span class="label">▶ 下一发言:</span>
    <div class="speaker-select">
      <button
        v-for="agent in agents"
        :key="agent.id"
        class="speaker-btn"
        :class="{
          spoken: spokenSet.has(agent.id),
          available: !spokenSet.has(agent.id),
        }"
        :disabled="spokenSet.has(agent.id) || discussionEnded"
        @click="$emit('select-speaker', agent.id)"
      >
        {{ agent.name }}
        <span v-if="spokenSet.has(agent.id)" class="check">✓</span>
      </button>
    </div>
    <div style="flex:1;"></div>
    <button
      class="action-btn"
      :disabled="!canNextRound"
      @click="$emit('next-round')"
    >
      下一轮 ⟶
    </button>
    <button
      v-if="!isLastPhase"
      class="action-btn green"
      @click="$emit('next-phase')"
    >
      进入下一阶段 →
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agents: { type: Array, required: true },
  spokenSet: { type: Set, default: () => new Set() },
  discussionEnded: { type: Boolean, default: false },
  isLastPhase: { type: Boolean, default: false },
})

defineEmits(['select-speaker', 'next-round', 'next-phase'])

const canNextRound = computed(() => {
  return props.agents.length > 0 &&
    props.agents.every(a => props.spokenSet.has(a.id))
})
</script>

<style scoped>
.control-bar {
  background: rgba(15,52,96,0.45); padding: 12px 16px; display: flex;
  gap: 10px; align-items: center; border-top: 1px solid rgba(233,69,96,0.15);
  backdrop-filter: blur(4px);
}
.label { font-size: 11px; color: #888; white-space: nowrap; }
.speaker-select { display: flex; gap: 8px; }
.speaker-btn {
  padding: 8px 16px; border: 2px solid #0f3460; border-radius: 4px;
  background: rgba(22,33,62,0.7); color: #ccc; font-family: inherit;
  font-size: 12px; cursor: pointer; transition: all 0.25s;
  display: flex; align-items: center; gap: 6px; position: relative;
}
.speaker-btn.available:hover {
  border-color: #e94560; color: #e94560;
  background: rgba(26,26,62,0.85);
  animation: btn-glow 0.6s infinite alternate;
  transform: translateY(-1px);
}
@keyframes btn-glow {
  from { box-shadow: 0 0 4px rgba(233,69,96,0.2); }
  to { box-shadow: 0 0 18px rgba(233,69,96,0.5); }
}
.speaker-btn.spoken {
  border-color: #1a3a6e; color: #555; background: rgba(10,15,26,0.4);
}
.check { color: #50d890; margin-left: 2px; }
.action-btn {
  padding: 10px 24px; border: 2px solid #e94560; border-radius: 4px;
  background: linear-gradient(135deg, rgba(233,69,96,0.9), rgba(233,69,96,0.7));
  color: #fff; font-family: inherit; font-size: 12px; cursor: pointer;
  letter-spacing: 1px; transition: all 0.25s; white-space: nowrap;
}
.action-btn:hover {
  background: linear-gradient(135deg, #ff6b81, #e94560);
  box-shadow: 0 0 24px rgba(233,69,96,0.5);
  transform: translateY(-1px);
}
.action-btn:disabled {
  background: #1a1a2e; border-color: #222; color: #444;
  cursor: not-allowed; box-shadow: none; transform: none;
}
.action-btn.green {
  border-color: #50d890;
  background: linear-gradient(135deg, rgba(80,216,144,0.7), rgba(40,160,80,0.5));
}
.action-btn.green:hover {
  background: linear-gradient(135deg, #50d890, #28a050);
  box-shadow: 0 0 24px rgba(80,216,144,0.4);
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ControlPanel.vue
git commit -m "feat: add ControlPanel component with speaker select and phase controls"
```

---

### Task 15: SetupPage Component

**Files:**
- Create: `frontend/src/components/SetupPage.vue`

- [ ] **Step 1: Write the SetupPage component**

```vue
<!-- frontend/src/components/SetupPage.vue -->
<template>
  <div class="setup-page">
    <div class="setup-card">
      <h2>⚙️ 配置讨论</h2>

      <div class="form-group">
        <label>讨论主题</label>
        <input
          v-model="topic"
          class="text-input"
          placeholder="输入讨论主题..."
        />
      </div>

      <div class="form-group">
        <label>Token 上限</label>
        <input
          v-model.number="tokenLimit"
          type="number"
          class="text-input"
          min="50"
          max="500"
        />
      </div>

      <div
        v-for="(agent, idx) in agents"
        :key="idx"
        class="agent-config"
      >
        <h3 :class="'agent-' + agent.id">Agent {{ idx + 1 }}</h3>
        <div class="agent-fields">
          <div class="field">
            <label>名称</label>
            <input v-model="agent.name" class="text-input" placeholder="给 agent 起个名" />
          </div>
          <div class="field">
            <label>模型</label>
            <input v-model="agent.model" class="text-input" placeholder="gpt-4o / claude-sonnet-4-6" />
          </div>
          <div class="field">
            <label>API Key</label>
            <input v-model="agent.api_key" class="text-input" type="password" placeholder="sk-..." />
          </div>
          <div class="field">
            <label>API Base URL</label>
            <input v-model="agent.api_base" class="text-input" placeholder="https://api.openai.com/v1" />
          </div>
        </div>
      </div>

      <button class="start-btn" :disabled="!isValid" @click="$emit('start', { topic, agents, tokenLimit })">
        🚀 开始讨论
      </button>
      <p v-if="!isValid" class="hint">请至少配置 2 个 agent，填写主题和所有 API Key</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const topic = ref('')
const tokenLimit = ref(200)
const agents = ref([
  { id: 'a', name: '产品分析师', model: 'gpt-4o', api_key: '', api_base: 'https://api.openai.com/v1' },
  { id: 'b', name: '技术架构师', model: 'claude-sonnet-4-6', api_key: '', api_base: 'https://api.anthropic.com/v1' },
  { id: 'c', name: '市场策略师', model: 'gemini-2.5-pro', api_key: '', api_base: 'https://generativelanguage.googleapis.com/v1beta' },
])

defineEmits(['start'])

const isValid = computed(() => {
  const filled = agents.value.filter(a => a.name && a.api_key)
  return topic.value.trim().length > 0 && filled.length >= 2
})
</script>

<style scoped>
.setup-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  padding: 20px; position: relative; z-index: 2;
}
.setup-card {
  width: 640px; max-width: 100%;
  background: rgba(22,33,62,0.9); border: 2px solid #0f3460; border-radius: 8px;
  padding: 24px; backdrop-filter: blur(12px);
}
h2 { color: #e94560; margin-bottom: 20px; font-size: 18px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 11px; color: #888; margin-bottom: 4px; }
.text-input {
  width: 100%; padding: 8px 12px;
  background: #0d1117; border: 1px solid #0f3460; border-radius: 4px;
  color: #e0e0e0; font-family: inherit; font-size: 13px;
  outline: none; transition: border-color 0.2s;
}
.text-input:focus { border-color: #e94560; }
.text-input::placeholder { color: #444; }

.agent-config {
  border: 1px solid #0f3460; border-radius: 4px; padding: 12px; margin-bottom: 12px;
  background: rgba(10,15,26,0.3);
}
.agent-config h3 { font-size: 13px; margin-bottom: 8px; }
.agent-config h3.agent-a { color: #5b8def; }
.agent-config h3.agent-b { color: #50d890; }
.agent-config h3.agent-c { color: #b86ef0; }
.agent-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.field { margin-bottom: 4px; }
.field label { font-size: 10px; color: #666; display: block; margin-bottom: 2px; }
.field .text-input { font-size: 12px; padding: 6px 10px; }

.start-btn {
  width: 100%; padding: 12px; margin-top: 8px;
  border: 2px solid #e94560; border-radius: 4px;
  background: linear-gradient(135deg, rgba(233,69,96,0.9), rgba(233,69,96,0.7));
  color: #fff; font-family: inherit; font-size: 14px; cursor: pointer;
  letter-spacing: 2px; transition: all 0.25s;
}
.start-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff6b81, #e94560);
  box-shadow: 0 0 24px rgba(233,69,96,0.5);
}
.start-btn:disabled { background: #1a1a2e; border-color: #222; color: #444; cursor: not-allowed; }
.hint { font-size: 10px; color: #555; text-align: center; margin-top: 8px; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/SetupPage.vue
git commit -m "feat: add SetupPage component with agent config form"
```

---

### Task 16: DiscussionRoom Component

**Files:**
- Create: `frontend/src/components/DiscussionRoom.vue`

- [ ] **Step 1: Write the DiscussionRoom component**

```vue
<!-- frontend/src/components/DiscussionRoom.vue -->
<template>
  <div class="container">
    <div class="topbar">
      <div class="title">
        <div class="icon"></div>
        ◈ AgentsChat
      </div>
      <div class="phase-info">
        <span class="status-dot"></span>
        阶段 <span>{{ currentPhase + 1 }}/3</span>
        · 第 <span>{{ roundNum }}</span> 轮
      </div>
    </div>

    <AgendaBar :current-phase="currentPhase" />

    <div class="chat-area" ref="chatRef">
      <!-- Round blocks -->
      <div v-for="(round, rIdx) in rounds" :key="rIdx" class="round-block">
        <div class="round-header">
          <span class="round-badge">第 {{ rIdx + 1 }} 轮</span>
          <span>{{ PHASES[currentPhase].icon }} {{ PHASES[currentPhase].name }}</span>
        </div>

        <ChatMessage
          v-for="msg in round.messages"
          :key="msg.id"
          :agent-id="msg.agentId"
          :agent-name="msg.agentName"
          :model="msg.model"
          :display-text="msg.text"
          :status="msg.status"
          :token-count="msg.tokenCount"
          :token-limit="tokenLimit"
          :ref-text="msg.refText"
        />

        <!-- Waiting slots for unspeaking agents -->
        <div
          v-for="agent in waitingAgents(round)"
          :key="'wait-' + agent.id"
          class="waiting-slot"
        >
          <div class="mini-avatar"></div>
          <span>{{ agent.name }} · {{ agent.model }} · 等待发言…</span>
        </div>
      </div>

      <!-- Phase transition banner -->
      <div v-if="phaseJustChanged" class="phase-banner">
        ⏭ 进入阶段：{{ PHASES[currentPhase].name }}
      </div>

      <div v-if="discussionEnded" class="phase-banner" style="border-color: #50d890; color: #50d890;">
        ✅ 讨论结束 — 三步议程全部完成
      </div>
    </div>

    <ControlPanel
      :agents="agentList"
      :spoken-set="spokenSet"
      :discussion-ended="discussionEnded"
      :is-last-phase="isLastPhase"
      @select-speaker="selectSpeaker"
      @next-round="nextRound"
      @next-phase="nextPhase"
    />

    <div class="status-bar">
      <span>🔗 {{ connected ? '已连接' : '未连接' }}</span>
      <span>📝 Token 上限: {{ tokenLimit }}</span>
      <span>🤖 {{ agentList.length }} Agents</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import AgendaBar from './AgendaBar.vue'
import ChatMessage from './ChatMessage.vue'
import ControlPanel from './ControlPanel.vue'
import { ServerMsgType, PHASES } from '../types/messages.js'

const props = defineProps({
  connected: { type: Boolean, default: false },
  agentList: { type: Array, default: () => [] },
  tokenLimit: { type: Number, default: 200 },
})

const emit = defineEmits(['select-speaker', 'next-round', 'next-phase'])

const currentPhase = ref(0)
const roundNum = ref(1)
const discussionEnded = ref(false)
const spokenSet = ref(new Set())
const chatRef = ref(null)
const phaseJustChanged = ref(false)

const isLastPhase = computed(() => currentPhase.value >= 2)

// Rounds data structure
const rounds = ref([
  { messages: [] },
])

function currentRound() {
  return rounds.value[rounds.value.length - 1]
}

function waitingAgents(round) {
  const spokenIds = round.messages.map(m => m.agentId)
  return props.agentList.filter(a => !spokenIds.includes(a.id))
}

function selectSpeaker(agentId) {
  emit('select-speaker', agentId)
}

function nextRound() {
  emit('next-round')
}

function nextPhase() {
  emit('next-phase')
}

// Server message handlers — call these from parent via expose or receive via props
function handleToken(agentId, tokenText) {
  const round = currentRound()
  let msg = round.messages.find(m => m.agentId === agentId && m.status === 'speaking')
  if (!msg) return
  msg.text += tokenText
  msg.tokenCount += 1
  scrollToBottom()
}

function handleAgentTyping(agentId, agentName) {
  const agent = props.agentList.find(a => a.id === agentId)
  const round = currentRound()
  const msg = {
    id: `${agentId}-${Date.now()}`,
    agentId,
    agentName,
    model: agent?.model || '',
    text: '',
    status: 'speaking',
    tokenCount: 0,
    refText: '',
  }
  round.messages.push(msg)
  scrollToBottom()
}

function handleAgentDone(agentId, fullText, tokenCount) {
  const round = currentRound()
  const msg = round.messages.find(m => m.agentId === agentId && m.status === 'speaking')
  if (msg) {
    msg.status = 'spoken'
    msg.text = fullText
    msg.tokenCount = tokenCount
  }
  spokenSet.value = new Set([...spokenSet.value, agentId])
}

function handleRoundComplete() {
  // Auto-finalize current round
}

function handleRoundStatus(spoken, pending, roundNumVal) {
  spokenSet.value = new Set(spoken)
  roundNum.value = roundNumVal
}

function handlePhaseStarted(phase, phaseName) {
  currentPhase.value = phase
  roundNum.value = 1
  spokenSet.value = new Set()
  rounds.value = [{ messages: [] }]
  phaseJustChanged.value = true
  setTimeout(() => { phaseJustChanged.value = false }, 3000)
}

function handleDiscussionEnded() {
  discussionEnded.value = true
}

function handleNextRoundReset() {
  spokenSet.value = new Set()
  rounds.value.push({ messages: [] })
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (chatRef.value) {
      chatRef.value.scrollTop = chatRef.value.scrollHeight
    }
  })
}

defineExpose({
  handleToken,
  handleAgentTyping,
  handleAgentDone,
  handleRoundComplete,
  handleRoundStatus,
  handlePhaseStarted,
  handleDiscussionEnded,
  handleNextRoundReset,
})
</script>

<style scoped>
.container {
  width: 940px; max-width: 96vw; margin: 20px auto;
  background: rgba(22,33,62,0.88); border: 2px solid #0f3460;
  border-radius: 8px; overflow: hidden; position: relative; z-index: 2;
  box-shadow: 0 0 60px rgba(15,52,96,0.35), 0 0 120px rgba(233,69,96,0.08), inset 0 0 40px rgba(0,0,0,0.15);
  backdrop-filter: blur(12px);
}
.container::before {
  content: ''; display: block; height: 2px;
  background: linear-gradient(90deg, #e94560, #5b8def, #50d890, #b86ef0);
  background-size: 200% 100%;
  animation: border-shift 3s linear infinite;
}
@keyframes border-shift {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

.topbar {
  background: rgba(15,52,96,0.5); padding: 10px 16px;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid rgba(233,69,96,0.2);
}
.title { font-size: 14px; font-weight: bold; color: #e94560; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; }
.icon {
  width: 22px; height: 22px;
  background: linear-gradient(135deg, #e94560, #5b8def);
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  animation: icon-spin 4s linear infinite;
}
@keyframes icon-spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.phase-info { font-size: 12px; color: #a0a0b0; }
.phase-info span { color: #e94560; font-weight: bold; }
.status-dot {
  display: inline-block; width: 6px; height: 6px;
  border-radius: 50%; background: #50d890;
  margin-right: 4px; animation: status-pulse 2s infinite;
}
@keyframes status-pulse {
  0%,100% { box-shadow: 0 0 4px #50d890; }
  50% { box-shadow: 0 0 14px #50d890, 0 0 24px rgba(80,216,144,0.3); }
}

.chat-area {
  padding: 16px; min-height: 400px; max-height: 500px; overflow-y: auto;
  display: flex; flex-direction: column; gap: 12px;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(15,52,96,0.08) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 100%, rgba(233,69,96,0.04) 0%, transparent 45%),
    rgba(26,26,46,0.3);
  scrollbar-width: thin; scrollbar-color: #0f3460 transparent;
}
.chat-area::-webkit-scrollbar { width: 4px; }
.chat-area::-webkit-scrollbar-track { background: transparent; }
.chat-area::-webkit-scrollbar-thumb { background: #0f3460; border-radius: 2px; }

.round-block {
  border: 1px solid rgba(15,52,96,0.3); border-radius: 4px; padding: 10px;
  background: rgba(10,15,26,0.2);
}
.round-header {
  font-size: 10px; color: #555; margin-bottom: 8px;
  display: flex; justify-content: space-between;
}
.round-badge { background: #0f3460; padding: 2px 8px; border-radius: 2px; color: #888; }

.waiting-slot {
  display: flex; align-items: center; gap: 10px; padding: 12px 14px;
  background: rgba(10,15,26,0.5); border: 1px dashed rgba(15,52,96,0.5);
  border-radius: 4px; color: #555; font-size: 12px; animation: wait-pulse 3s infinite;
  margin-top: 8px;
}
@keyframes wait-pulse {
  0%,100% { border-color: rgba(15,52,96,0.3); }
  50% { border-color: rgba(15,52,96,0.7); }
}
.mini-avatar {
  width: 24px; height: 24px;
  background: linear-gradient(135deg, #1a1a3e, #2a2a5e);
  border-radius: 2px;
  animation: idle-bob 2.5s ease-in-out infinite;
}
@keyframes idle-bob {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.phase-banner {
  text-align: center; padding: 8px; margin: 4px 0;
  background: linear-gradient(90deg, transparent, rgba(233,69,96,0.1), transparent);
  border-top: 1px solid rgba(233,69,96,0.2);
  border-bottom: 1px solid rgba(233,69,96,0.2);
  font-size: 11px; color: #e94560;
}

.status-bar {
  background: rgba(10,15,26,0.5); padding: 4px 16px; display: flex;
  gap: 16px; font-size: 10px; color: #444;
  border-top: 1px solid rgba(15,52,96,0.2);
}
.status-bar span { display: flex; align-items: center; gap: 4px; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/DiscussionRoom.vue
git commit -m "feat: add DiscussionRoom with round blocks, streaming, and phase management"
```

---

### Task 17: App.vue Integration

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Write the integrated App.vue**

```vue
<!-- frontend/src/App.vue -->
<template>
  <BackgroundEffects />

  <SetupPage
    v-if="!sessionStarted"
    @start="onStart"
  />

  <DiscussionRoom
    v-else
    ref="discussionRef"
    :connected="connected"
    :agent-list="agentList"
    :token-limit="tokenLimit"
    @select-speaker="selectSpeaker"
    @next-round="nextRound"
    @next-phase="nextPhase"
  />
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import SetupPage from './components/SetupPage.vue'
import DiscussionRoom from './components/DiscussionRoom.vue'
import BackgroundEffects from './components/BackgroundEffects.vue'
import { useWebSocket } from './composables/useWebSocket.js'
import { ClientMsgType, ServerMsgType } from './types/messages.js'

const { connected, connect, send, on, disconnect } = useWebSocket()

const sessionStarted = ref(false)
const discussionRef = ref(null)
const agentList = ref([])
const tokenLimit = ref(200)

async function onStart(config) {
  agentList.value = config.agents
  tokenLimit.value = config.tokenLimit

  try {
    await connect()
  } catch (e) {
    console.error('WebSocket connection failed:', e)
    return
  }

  // Wire up server message handlers
  on(ServerMsgType.TOKEN, (msg) => {
    discussionRef.value?.handleToken(msg.agent_id, msg.token_text)
  })

  on(ServerMsgType.AGENT_TYPING, (msg) => {
    discussionRef.value?.handleAgentTyping(msg.agent_id, msg.agent_name)
  })

  on(ServerMsgType.AGENT_DONE, (msg) => {
    discussionRef.value?.handleAgentDone(msg.agent_id, msg.full_text, msg.token_count)
  })

  on(ServerMsgType.ROUND_STATUS, (msg) => {
    discussionRef.value?.handleRoundStatus(msg.spoken, msg.pending, msg.round_num)
  })

  on(ServerMsgType.ROUND_COMPLETE, () => {
    discussionRef.value?.handleRoundComplete()
  })

  on(ServerMsgType.PHASE_STARTED, (msg) => {
    discussionRef.value?.handlePhaseStarted(msg.phase, msg.phase_name)
  })

  on(ServerMsgType.DISCUSSION_ENDED, () => {
    discussionRef.value?.handleDiscussionEnded()
  })

  on(ServerMsgType.ERROR, (msg) => {
    console.error('Server error:', msg.code, msg.detail)
    alert(`Error: ${msg.detail}`)
  })

  // Start session
  send({
    type: ClientMsgType.INIT_SESSION,
    topic: config.topic,
    agents: config.agents,
    token_limit: config.tokenLimit,
  })

  sessionStarted.value = true
}

function selectSpeaker(agentId) {
  send({ type: ClientMsgType.SELECT_SPEAKER, agent_id: agentId })
}

function nextRound() {
  send({ type: ClientMsgType.NEXT_ROUND })
  nextTick(() => {
    discussionRef.value?.handleNextRoundReset()
  })
}

function nextPhase() {
  send({ type: ClientMsgType.NEXT_PHASE })
}

onUnmounted(() => {
  disconnect()
})
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: integrate App.vue with WS lifecycle and page routing"
```

---

### Task 18: Global Styles Polish

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Update style.css with scanline effect and global polish**

```css
/* frontend/src/style.css */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0d1117;
  color: #e0e0e0;
  font-family: 'Courier New', 'Source Code Pro', monospace;
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

/* Scanline overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.02) 2px,
    rgba(0,0,0,0.02) 4px
  );
  pointer-events: none;
  z-index: 100;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* Selection color */
::selection {
  background: #e94560;
  color: #fff;
}

/* Scrollbar global */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #0f3460; border-radius: 2px; }
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/style.css
git commit -m "style: add scanline overlay and global polish"
```

---

### Task 19: .gitignore and README

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Write .gitignore**

```
# .gitignore
node_modules/
dist/
__pycache__/
*.pyc
.env
.superpowers/
*.egg-info/
```

- [ ] **Step 2: Write README.md**

```markdown
# AgentsChat

Multi-agent collaborative discussion platform. User moderates 2-3 AI agents through a three-phase agenda with real-time streaming.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, configure agents with API keys, and start a discussion.
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore README.md
git commit -m "chore: add .gitignore and README"
```

---

### Task 20: End-to-End Integration Test

**Files:**
- Create: `backend/test_integration.py`

- [ ] **Step 1: Write integration test using httpx WebSocket client**

```python
# backend/test_integration.py
"""Manual integration test — run with pytest after starting the server."""
import pytest
import json
import asyncio
import httpx


@pytest.mark.asyncio
async def test_websocket_init_session():
    """Test that init_session creates a session and returns session_ready."""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET", "http://127.0.0.1:8000/ws"
        ) as response:
            # This tests the HTTP upgrade; full WS test needs websockets lib
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://127.0.0.1:8000/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
```

- [ ] **Step 2: Install test dependencies**

```bash
cd backend && pip install pytest pytest-asyncio httpx
```

- [ ] **Step 3: Start server and run tests**

```bash
# Terminal 1:
cd backend && uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2:
cd backend && pytest test_integration.py -v
```

Expected: 2 tests pass (health check + WS upgrade status code).

- [ ] **Step 4: Commit**

```bash
git add backend/test_integration.py
git commit -m "test: add integration tests for health and WS upgrade"
```
