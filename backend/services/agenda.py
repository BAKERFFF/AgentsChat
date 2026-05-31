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
    def get_base_prompt(phase_index: int) -> str:
        """Get the phase system prompt without agent name."""
        return AgendaEngine.get_phase(phase_index).system_prompt

    @staticmethod
    def get_system_prompt(phase_index: int, agent_name: str) -> str:
        phase = AgendaEngine.get_phase(phase_index)
        return f"{phase.system_prompt}\n你的名字是{agent_name}。当前讨论主题和完整对话历史已提供。"
