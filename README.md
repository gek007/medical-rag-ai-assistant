# Medical RAG AI Assistant

A role-based RAG (Retrieval-Augmented Generation) system for medical documents, built with FastAPI, Pinecone, and OpenAI.

## Architecture

```
server/
├── auth/               # Authentication (HTTP Basic Auth, bcrypt)
│   ├── routes.py       # /signup, /login endpoints
│   ├── models.py       # Pydantic request models
│   └── hash_utils.py   # Password hashing
├── docs/               # Document ingestion pipeline
│   ├── routes.py       # /upload endpoint
│   └── vectorstore.py  # PDF → chunks → embeddings → Pinecone
├── config/
│   ├── db.py           # MongoDB connection
│   └── logger.py       # Centralized logging (console + rotating file)
├── logs/               # Runtime log output (auto-created)
├── uploaded_docs/      # Temporary PDF storage (auto-created)
├── main.py             # FastAPI app + request/response middleware
├── pyproject.toml      # Dependencies (uv)
└── .env.example        # Environment variable template
```

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Auth | HTTP Basic Auth + bcrypt |
| Database | MongoDB Atlas |
| Embeddings | OpenAI `text-embedding-3-small` (768 dims) |
| Vector Store | Pinecone (serverless) |
| PDF Parsing | LangChain + PyPDF |
| Package Manager | uv |

## Setup

### 1. Install dependencies

```bash
cd server
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run

```bash
uv run main.py
```

Server starts at `http://localhost:8000`

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| POST | `/signup` | None | Register user (`role`: `admin` or `doctor`) |
| GET | `/login` | Basic Auth | Verify credentials |
| POST | `/upload` | Basic Auth (admin only) | Upload PDF → embed → store in Pinecone |

## Environment Variables

See `.env.example` for all required variables:

- `OPENAI_API_KEY` — for `text-embedding-3-small`
- `GOOGLE_API_KEY` — reserved for future use
- `MONGO_URI` — MongoDB Atlas connection string
- `DB_NAME` — MongoDB database name
- `PINECONE_API_KEY` — Pinecone API key
- `PINECONE_ENVIRONMENT` — Pinecone region (e.g. `us-east-1`)
- `PINECONE_INDEX_NAME` — Pinecone index name (e.g. `medical-rag`)


===================== How to create users ==========================

1. \Signup : admin/docotor/user

2. \login  (role = admin)

   user: super 
   passw: pass123
   role: admin 

3. Chat /chat (role doctor)

   user: man 
   passw: pass123  
   role: doctor   

=================== !!!!!!!!!!!!!!!!!!!!!! =======================


