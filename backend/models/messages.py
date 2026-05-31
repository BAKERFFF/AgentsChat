from pydantic import BaseModel, Field
from typing import Optional


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
