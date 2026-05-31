<template>
  <BackgroundEffects />

  <SetupPage
    v-if="!sessionStarted"
    @start="onStart"
  />

  <DiscussionRoom
    v-else
    ref="discussionRef"
    :connected="connected"
    :agent-list="agentList"
    :token-limit="tokenLimit"
    @select-speaker="selectSpeaker"
    @next-round="nextRound"
    @next-phase="nextPhase"
  />
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import SetupPage from './components/SetupPage.vue'
import DiscussionRoom from './components/DiscussionRoom.vue'
import BackgroundEffects from './components/BackgroundEffects.vue'
import { useWebSocket } from './composables/useWebSocket.js'
import { ClientMsgType, ServerMsgType } from './types/messages.js'

const { connected, connect, send, on, disconnect } = useWebSocket()

const sessionStarted = ref(false)
const discussionRef = ref(null)
const agentList = ref([])
const tokenLimit = ref(200)

async function onStart(config) {
  agentList.value = config.agents
  tokenLimit.value = config.tokenLimit

  try {
    await connect()
  } catch (e) {
    console.error('WebSocket connection failed:', e)
    return
  }

  on(ServerMsgType.TOKEN, (msg) => {
    discussionRef.value?.handleToken(msg.agent_id, msg.token_text)
  })

  on(ServerMsgType.AGENT_TYPING, (msg) => {
    discussionRef.value?.handleAgentTyping(msg.agent_id, msg.agent_name)
  })

  on(ServerMsgType.AGENT_DONE, (msg) => {
    discussionRef.value?.handleAgentDone(msg.agent_id, msg.full_text, msg.token_count)
  })

  on(ServerMsgType.ROUND_STATUS, (msg) => {
    discussionRef.value?.handleRoundStatus(msg.spoken, msg.pending, msg.round_num)
  })

  on(ServerMsgType.ROUND_COMPLETE, () => {
    discussionRef.value?.handleRoundComplete()
  })

  on(ServerMsgType.PHASE_STARTED, (msg) => {
    discussionRef.value?.handlePhaseStarted(msg.phase, msg.phase_name)
  })

  on(ServerMsgType.DISCUSSION_ENDED, () => {
    discussionRef.value?.handleDiscussionEnded()
  })

  on(ServerMsgType.ERROR, (msg) => {
    console.error('Server error:', msg.code, msg.detail)
    alert(`Error: ${msg.detail}`)
  })

  send({
    type: ClientMsgType.INIT_SESSION,
    topic: config.topic,
    agents: config.agents,
    token_limit: config.tokenLimit,
  })

  sessionStarted.value = true
}

function selectSpeaker(agentId) {
  send({ type: ClientMsgType.SELECT_SPEAKER, agent_id: agentId })
}

function nextRound() {
  send({ type: ClientMsgType.NEXT_ROUND })
  nextTick(() => {
    discussionRef.value?.handleNextRoundReset()
  })
}

function nextPhase() {
  send({ type: ClientMsgType.NEXT_PHASE })
}

onUnmounted(() => {
  disconnect()
})
</script>
