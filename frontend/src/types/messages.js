export const ClientMsgType = {
  INIT_SESSION: 'init_session',
  SELECT_SPEAKER: 'select_speaker',
  NEXT_PHASE: 'next_phase',
  NEXT_ROUND: 'next_round',
}

export const ServerMsgType = {
  SESSION_READY: 'session_ready',
  PHASE_STARTED: 'phase_started',
  AGENT_TYPING: 'agent_typing',
  TOKEN: 'token',
  AGENT_DONE: 'agent_done',
  ROUND_STATUS: 'round_status',
  ROUND_COMPLETE: 'round_complete',
  DISCUSSION_ENDED: 'discussion_ended',
  ERROR: 'error',
}

export const PHASES = [
  { index: 0, name: '分析问题', icon: '🔍' },
  { index: 1, name: '讨论问题', icon: '💬' },
  { index: 2, name: '得出结论', icon: '📋' },
]
