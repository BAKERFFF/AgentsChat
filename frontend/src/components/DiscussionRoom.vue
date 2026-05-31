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

        <div
          v-for="agent in waitingAgents(round)"
          :key="'wait-' + agent.id"
          class="waiting-slot"
        >
          <div class="mini-avatar"></div>
          <span>{{ agent.name }} · {{ agent.model }} · 等待发言…</span>
        </div>
      </div>

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
import { ref, computed, nextTick } from 'vue'
import AgendaBar from './AgendaBar.vue'
import ChatMessage from './ChatMessage.vue'
import ControlPanel from './ControlPanel.vue'
import { PHASES } from '../types/messages.js'

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

function handleRoundComplete() {}

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
