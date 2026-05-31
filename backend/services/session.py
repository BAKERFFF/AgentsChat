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
        return agent_id in self.agents and agent_id not in self.spoken_this_round

    def mark_spoken(self, agent_id: str) -> None:
        self.spoken_this_round.add(agent_id)

    def all_spoken(self) -> bool:
        return self.spoken_this_round == set(self.agents.keys())

    def reset_round(self) -> None:
        self.spoken_this_round.clear()
        self.current_round += 1

    def pending_agents(self) -> list[str]:
        return [aid for aid in self.agents if aid not in self.spoken_this_round]

    def spoken_agents(self) -> list[str]:
        return list(self.spoken_this_round)

    def record_message(self, agent_id: str, content: str) -> None:
        agent = self.agents[agent_id]
        self.conversation_history.append({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "content": content,
        })

    def is_expired(self, timeout_seconds: int = 300) -> bool:
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
        expired = [
            sid for sid, s in self._sessions.items()
            if s.is_expired(timeout_seconds)
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


session_store = SessionStore()
