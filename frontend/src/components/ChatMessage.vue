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
  status: { type: String, default: 'waiting' },
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
