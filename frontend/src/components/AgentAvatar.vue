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
