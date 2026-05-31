# AgentsChat

Multi-agent collaborative discussion platform. User moderates 2-3 AI agents through a three-phase agenda with real-time streaming.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, configure agents with API keys, and start a discussion.
