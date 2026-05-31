from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(title="AgentsChat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "hello"})
    await websocket.close()
