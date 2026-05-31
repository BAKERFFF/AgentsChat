import json
import traceback
from fastapi import WebSocket, WebSocketDisconnect
from models.messages import (
    ClientMessage, ServerMessage, AgentConfig,
    ClientMsgType, ServerMsgType,
)
from services.session import session_store
from services.agenda import AgendaEngine
from services.llm_proxy import llm_proxy


async def handle_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id: str | None = None

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg = ClientMessage(**data)
            except Exception:
                await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INVALID_JSON", "detail": "Invalid message format"})
                continue

            if msg.type == ClientMsgType.INIT_SESSION:
                session_id = await handle_init(websocket, msg)

            elif msg.type == ClientMsgType.SELECT_SPEAKER:
                await handle_select_speaker(websocket, session_id, msg)

            elif msg.type == ClientMsgType.NEXT_ROUND:
                await handle_next_round(websocket, session_id)

            elif msg.type == ClientMsgType.NEXT_PHASE:
                await handle_next_phase(websocket, session_id)

            else:
                await websocket.send_json({"type": ServerMsgType.ERROR, "code": "UNKNOWN_TYPE", "detail": f"Unknown message type: {msg.type}"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        traceback.print_exc()
        try:
            await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INTERNAL", "detail": str(e)})
        except Exception:
            pass
    finally:
        if session_id:
            session_store.delete(session_id)


async def handle_init(websocket: WebSocket, msg: ClientMessage) -> str:
    if not msg.topic:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "MISSING_TOPIC", "detail": "Topic is required"})
        return ""

    if not msg.agents or len(msg.agents) < 2 or len(msg.agents) > 3:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "INVALID_AGENTS", "detail": "Need 2-3 agents"})
        return ""

    token_limit = msg.token_limit or 200
    session = session_store.create(msg.topic, msg.agents, token_limit)
    phase = AgendaEngine.get_phase(0)

    await websocket.send_json({
        "type": ServerMsgType.SESSION_READY,
        "session_id": session.session_id,
    })
    await websocket.send_json({
        "type": ServerMsgType.PHASE_STARTED,
        "phase": 0,
        "phase_name": phase.name,
        "system_prompt_hint": phase.system_prompt[:100],
    })
    await send_round_status(websocket, session)

    return session.session_id


async def handle_select_speaker(websocket: WebSocket, session_id: str | None, msg: ClientMessage) -> None:
    if not session_id:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "NO_SESSION", "detail": "Session not initialized"})
        return

    session = session_store.get(session_id)
    if not session:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "SESSION_NOT_FOUND", "detail": "Session expired or not found"})
        return

    agent_id = msg.agent_id
    if not agent_id:
        await websocket.send_json({"type": ServerMsgType.ERROR, "code": "MISSING_AGENT_ID", "detail": "agent_id is required"})
        return

    if not session.can_speak(agent_id):
        pending = session.pending_agents()
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "ALREADY_SPOKEN",
            "detail": f"Agent has already spoken this round. Available: {pending}",
        })
        return

    agent = session.agents[agent_id]
    phase_prompt = AgendaEngine.get_system_prompt(session.current_phase, agent.name)

    await websocket.send_json({
        "type": ServerMsgType.AGENT_TYPING,
        "agent_id": agent_id,
        "agent_name": agent.name,
    })

    full_text = ""
    token_count = 0
    try:
        async for token in llm_proxy.stream_response(
            agent=agent,
            conversation_history=session.conversation_history,
            system_prompt=phase_prompt,
            token_limit=session.token_limit,
        ):
            full_text += token
            token_count += 1
            await websocket.send_json({
                "type": ServerMsgType.TOKEN,
                "agent_id": agent_id,
                "token_text": token,
            })
    except Exception as e:
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "LLM_ERROR",
            "detail": f"Agent '{agent.name}' call failed: {str(e)}",
        })
        return

    session.record_message(agent_id, full_text)
    session.mark_spoken(agent_id)

    await websocket.send_json({
        "type": ServerMsgType.AGENT_DONE,
        "agent_id": agent_id,
        "full_text": full_text,
        "token_count": token_count,
    })

    if session.all_spoken():
        round_summary = f"第{session.current_round}轮完成，所有agent已发言。"
        await websocket.send_json({
            "type": ServerMsgType.ROUND_COMPLETE,
            "round_summary": round_summary,
        })
    else:
        await send_round_status(websocket, session)


async def handle_next_round(websocket: WebSocket, session_id: str | None) -> None:
    if not session_id:
        return
    session = session_store.get(session_id)
    if not session:
        return

    if not session.all_spoken():
        await websocket.send_json({
            "type": ServerMsgType.ERROR,
            "code": "ROUND_NOT_COMPLETE",
            "detail": f"Not all agents have spoken. Pending: {session.pending_agents()}",
        })
        return

    session.reset_round()
    await send_round_status(websocket, session)


async def handle_next_phase(websocket: WebSocket, session_id: str | None) -> None:
    if not session_id:
        return
    session = session_store.get(session_id)
    if not session:
        return

    next_index = session.current_phase + 1

    if AgendaEngine.is_last_phase(session.current_phase):
        await websocket.send_json({
            "type": ServerMsgType.DISCUSSION_ENDED,
            "phases_summary": f"三步议程全部完成。共{session.current_round}轮讨论。",
        })
        session.discussion_ended = True
        return

    session.current_phase = next_index
    session.spoken_this_round.clear()
    session.current_round = 1

    phase = AgendaEngine.get_phase(next_index)
    await websocket.send_json({
        "type": ServerMsgType.PHASE_STARTED,
        "phase": next_index,
        "phase_name": phase.name,
        "system_prompt_hint": phase.system_prompt[:100],
    })
    await send_round_status(websocket, session)


async def send_round_status(websocket: WebSocket, session) -> None:
    await websocket.send_json({
        "type": ServerMsgType.ROUND_STATUS,
        "spoken": session.spoken_agents(),
        "pending": session.pending_agents(),
        "round_num": session.current_round,
    })
