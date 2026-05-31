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
        # 把讨论主题作为初始消息写入历史
        self.conversation_history.append({
            "agent_id": "system",
            "agent_name": "主持人",
            "content": f"讨论主题：{topic}",
            "round": 0,
            "is_phase_marker": False,
        })

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
            "round": self.current_round,
            "is_phase_marker": False,
        })

    def record_phase_marker(self, phase_index: int, phase_name: str) -> None:
        """Record a phase transition in conversation history so models know context changed."""
        self.conversation_history.append({
            "agent_id": "system",
            "agent_name": "系统",
            "content": f"【进入新阶段：{phase_name}】请基于之前的全部讨论历史，以新阶段的视角继续发言。",
            "round": 0,
            "is_phase_marker": True,
        })

    def get_current_round_messages(self) -> list[dict]:
        """Get messages from the current round (excluding system/markers)."""
        return [
            m for m in self.conversation_history
            if m["round"] == self.current_round and not m.get("is_phase_marker") and m["agent_id"] != "system"
        ]

    def is_last_speaker(self) -> bool:
        """Check if the next speaker will be the last one in this round."""
        return len(self.spoken_this_round) == len(self.agents) - 1

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
