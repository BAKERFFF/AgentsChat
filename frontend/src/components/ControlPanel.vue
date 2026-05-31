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
