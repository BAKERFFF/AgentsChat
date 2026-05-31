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
