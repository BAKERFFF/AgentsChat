# AgentsChat 设计文档

> 一个让多个 AI agent 进行协同讨论的 Web 平台。用户作为主持人，设定三步议程，手动控制发言顺序，观看 agent 实时流式辩论。

## 1. 概述

### 1.1 核心场景

- 用户提出一个话题，设定三步议程（分析问题 → 讨论问题 → 得出结论）
- 2-3 个 AI agent 围绕议程展开辩论式讨论
- 用户手动选择每个 agent 的发言顺序，掌控讨论节奏
- 实时流式展示 agent 输出，token 上限 200，高效精辟

### 1.2 关键约束

| 约束 | 值 |
|------|-----|
| Agent 数量 | 2-3 个 |
| Token 上限 | 200 / 次发言 |
| 每轮发言规则 | 每个 agent 强制发言一次 |
| 持久化 | 无，纯临时会话 |
| LLM 后端 | 用户自带 API Key（OpenAI / Anthropic） |
| 技术栈 | Vue 3 + FastAPI (Python) |
| 通信方式 | WebSocket（单一双工通道） |

### 1.3 Agent 定义

- Agent 是纯 AI 模型实例，无预设角色/人设
- 用户可自定义每个 agent 的名称和模型
- 不同 agent 可选用不同模型（GPT-4o / Claude / Gemini 等）

## 2. 架构

```
┌─────────────────────────────────────────────────────┐
│                    Vue 3 SPA (浏览器)                 │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ 配置页    │  │ 讨论室    │  │ 主持人控制面板       │ │
│  │ Agent设置 │  │ 流式展示  │  │ 发言选择/轮次/阶段   │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│                        │ WebSocket                   │
└────────────────────────┼────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────┐
│                  FastAPI Server                       │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Session Mgr │  │ LLM Proxy│  │ Agenda Engine  │  │
│  │ (内存状态)   │  │ (流式调用)│  │ (3步议程+轮次)  │  │
│  └─────────────┘  └──────────┘  └────────────────┘  │
│                         │                            │
└─────────────────────────┼────────────────────────────┘
                          │ HTTP Stream
                    ┌─────┴─────┐
                    │ OpenAI /  │
                    │ Anthropic │
                    └───────────┘
```

### 2.1 服务端组件

```
FastAPI Server
├── main.py              — FastAPI 入口，挂载 WebSocket 路由
├── config.py            — 全局配置（CORS、默认 token 上限等）
├── ws/chat.py           — WebSocket 端点，消息路由分发
├── services/
│   ├── session.py       — 内存会话管理（创建、销毁、状态读写）
│   ├── llm_proxy.py     — LLM 调用封装（统一接口、流式转发、token 截断）
│   └── agenda.py        — 三步议程推进 + 轮次管理
└── models/
    └── messages.py      — WebSocket 消息类型定义（Pydantic）
```

| 组件 | 职责 | 依赖 |
|------|------|------|
| `session.py` | 保存/读取会话：agent 列表、议程状态、对话历史、当前阶段、当前轮发言记录 | 无 |
| `llm_proxy.py` | 接收 agent 配置 + 对话上下文，调用对应 LLM API，流式返回 token，200 token 硬截断 | 无 |
| `agenda.py` | 三步议程推进（阶段切换）、轮次重置、判断 `round_complete` | session |
| `ws/chat.py` | WebSocket 连接管理、消息分发、调用 service 层 | session, llm_proxy, agenda |

## 3. WebSocket 协议

### 3.1 客户端 → 服务端

| 消息类型 | 携带数据 | 说明 |
|---------|---------|------|
| `init_session` | `{topic, agents, agenda_phases, token_limit}` | 初始化讨论会话。topic 为讨论主题，agents 含 name/model/api_key，agenda_phases 固定为三步 |
| `select_speaker` | `{agent_id}` | 用户选择下一个发言的 agent（从未发言列表中选） |
| `next_phase` | — | 进入下一议程阶段（分析→讨论→结论） |
| `next_round` | — | 同一阶段内开启新一轮（发言记录重置） |

### 3.2 服务端 → 客户端

| 消息类型 | 携带数据 | 说明 |
|---------|---------|------|
| `session_ready` | `{session_id}` | 会话初始化完成 |
| `phase_started` | `{phase, phase_name, system_prompt_hint}` | 新阶段开始 |
| `agent_typing` | `{agent_id, agent_name}` | 某个 agent 开始生成回复 |
| `token` | `{agent_id, token_text}` | 流式输出的单个 token |
| `agent_done` | `{agent_id, full_text, token_count}` | agent 发言完成（达上限或自然结束） |
| `round_status` | `{spoken[], pending[], round_num}` | 本轮发言状态 |
| `round_complete` | `{round_summary}` | 所有 agent 都已发言，本轮自动结束 |
| `discussion_ended` | `{phases_summary}` | 三步议程全部完成 |
| `error` | `{code, detail}` | 错误信息 |

### 3.3 交互流程

```
用户 init_session → session_ready
用户 select_speaker(A) → agent_typing → token... → agent_done → round_status
用户 select_speaker(B) → agent_typing → token... → agent_done → round_status
用户 select_speaker(C) → agent_typing → token... → agent_done → round_complete
用户 next_round → round_status(重置)
  ... (多轮) ...
用户 next_phase → phase_started(讨论) → round_status(重置)
  ... (多轮) ...
用户 next_phase → phase_started(结论) → round_status(重置)
  ... (最后一轮) ...
→ discussion_ended
```

## 4. 三步议程系统

### 4.1 阶段定义

| 阶段 | 名称 | System Prompt 导向 |
|------|------|-------------------|
| 1 | 🔍 分析问题 | 从你的视角拆解问题。引用并回应其他 agent 的观点，形成辩论式分析。每个 agent 必须结合对话历史给出新见解。 |
| 2 | 💬 讨论问题 | 就分析阶段涌现的关键分歧和共识展开深入讨论。挑战对方的假设，为你的立场辩护，碰撞出解决方案。 |
| 3 | 📋 得出结论 | 综合全程讨论，给出你的最终判断。明确标注共识点和保留的个人意见。 |

### 4.2 分析阶段的辩论规则

- 每个 agent 发言时必须引用/回应之前 agent 的观点
- LLM 调用时传入完整对话历史作为 context
- 前端渲染时显示引用关系（↩ 回应xxx：yyy维度）
- Token 上限 200 强制精炼表达

### 4.3 阶段推进

- 用户在任何阶段内可进行多轮讨论
- 用户手动触发 `next_phase` 推进到下一阶段
- 阶段推进不可逆
- 所有三步完成后，讨论自动结束

## 5. Agent 配置

### 5.1 可配置项

```json
{
  "id": "a",
  "name": "产品分析师",
  "model": "gpt-4o",
  "api_key": "sk-...",
  "api_base": "https://api.openai.com/v1"
}
```

### 5.2 改名功能

- 配置页中每个 agent 的名称可自由编辑
- 名称贯穿头像旁、消息气泡、控制按钮、等待区
- 名称仅影响前端展示和 prompt 中的角色标识，不影响模型行为

## 6. 前端 UI

### 6.1 页面结构

| 页面 | 功能 |
|------|------|
| 配置页 | 设置讨论主题、三个 agent 的名称/模型/API Key、token 上限 |
| 讨论室 | 实时流式展示区 + 议程进度 + 主持人控制面板 |

### 6.2 讨论室布局

```
┌─────────────────────────────────────────────┐
│  ◈ AgentsChat           阶段 1/3 · 第 2 轮  │
├─────────────────────────────────────────────┤
│  ✓ 分析问题  │  ▶ 讨论问题  │  得出结论      │
├─────────────────────────────────────────────┤
│  ┌── 第 1 轮 ────────────────────────────┐  │
│  │  [头像A] 产品分析师                    │  │
│  │  ↩ 回应市场策略师：信任度问题          │  │
│  │  我认为系统应该在过滤和透明度之间...   │  │
│  │                          187/200 tokens │  │
│  │  [头像B] 技术架构师 ● 正在输入...      │  │
│  │  ...流式输出中...                      │  │
│  │  [头像C] 市场策略师 · 等待发言         │  │
│  └──────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│  ▶ 下一发言: [产品✓] [技术✓] [市场] [下一轮]│
└─────────────────────────────────────────────┘
```

### 6.3 视觉风格

- **主题**：暗色赛博朋克风格（深蓝底 + 霓虹红强调色）
- **字体**：等宽字体（Courier New / Source Code Pro）
- **头像**：三个独特 CSS 像素机器人（蓝方块 / 绿圆形 / 紫三角）
- **背景**：网格底纹 + 5 个浮动渐变光球 + 30 个粒子流 + 扫描线
- **动画**：发言者弹跳 + 光标闪烁 + 按钮脉冲发光 + 等待区浮动 + 消息滑入

## 7. 错误处理

| 场景 | 处理方式 |
|------|---------|
| LLM API 调用失败 | 发送 `error` 消息，不中断会话，用户可重新选择该 agent |
| API Key 无效 | `init_session` 阶段校验，失败则拒绝建连 |
| 网络断开 | 前端提示重连，后端保留会话状态 5 分钟后清理 |
| Token 超限 | 硬截断并发送 `agent_done`，前端显示 `200/200 tokens` |
| 重复选择已发言 agent | 服务端拒绝，返回 `error` 并提示可选 agent 列表 |

## 8. 非目标（YAGNI）

- ❌ 用户账户/登录系统
- ❌ 讨论历史持久化和回放
- ❌ Agent 角色模板库
- ❌ 多租户/多会话并行
- ❌ Agent 配备工具/插件
- ❌ 浏览器外的部署方式
- ❌ 国际化

## 9. 文件结构

```
AgentsChat/
├── frontend/                  # Vue 3 SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── SetupPage.vue       # Agent 配置页
│   │   │   ├── DiscussionRoom.vue  # 讨论室主组件
│   │   │   ├── AgentAvatar.vue     # 像素头像组件
│   │   │   ├── ChatMessage.vue     # 消息气泡组件
│   │   │   ├── AgendaBar.vue       # 三步议程进度
│   │   │   ├── ControlPanel.vue    # 主持人控制面板
│   │   │   └── BackgroundEffects.vue # 背景粒子/光球
│   │   ├── composables/
│   │   │   └── useWebSocket.js     # WebSocket 连接管理
│   │   ├── types/
│   │   │   └── messages.js         # 消息类型定义
│   │   ├── App.vue
│   │   └── main.js
│   └── index.html
├── backend/                   # FastAPI
│   ├── main.py
│   ├── config.py
│   ├── ws/
│   │   └── chat.py
│   ├── services/
│   │   ├── session.py
│   │   ├── llm_proxy.py
│   │   └── agenda.py
│   └── models/
│       └── messages.py
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-31-agentschat-design.md
```
