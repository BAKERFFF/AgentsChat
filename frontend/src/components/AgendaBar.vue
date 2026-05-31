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
