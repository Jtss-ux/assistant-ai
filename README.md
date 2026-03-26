# Zoo Tour Guide AI Agent
### Gen AI Academy APAC Edition — Track 1: Build and Deploy AI Agents

**Author:** Joseph Thomas Stalin · josephst2007@gmail.com  
**Lab:** GSP532 — Build a Smart Cloud Application with Vibe Coding and MCP  
**Score:** ✅ 100/100 (all checkpoints passed)

---

## 🦒 What Is This?

The **Zoo Tour Guide** is a production-ready AI agent built with the **Google Agent Development Kit (ADK)** and **Gemini**, deployed as a containerised service on **Google Cloud Run**. It answers visitor questions about Cloud Creek Zoo's animals by combining:

- 🔌 **Zoo MCP Server** — a custom FastMCP server deployed on Cloud Run that exposes real-time zoo animal data
- ✨ **Gemini** (via Vertex AI) — the LLM backbone for natural language understanding and response generation
- ☁️ **Cloud Run** — serverless, scalable hosting for both the MCP server and the ADK agent

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Cloud Run ADK Agent  ──────►  Gemini (Vertex AI)
    │                              │
    ▼                              │
MCP Toolset  ◄─────────────────────┘
    │
    ▼
MCP Server (Cloud Run)
    │
    ▼
Zoo Animal Database
```

**Services deployed:**
| Service | Cloud Run Name | Description |
|---|---|---|
| MCP Server | `coding-zoo-mcp-server` | Zoo data API via FastMCP protocol |
| ADK Agent | `coding-zoo-tour-guide` | Tour guide with web UI (`--with_ui`) |

---

## 🚀 Local Setup

### Prerequisites

- Python 3.11+
- `gcloud` CLI authenticated
- Vertex AI API enabled

### Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cd zoo_guide_agent
cat <<EOF > .env
MODEL="gemini-1.5-flash-001"
MCP_SERVER_URL="https://<your-mcp-server>.run.app/mcp/"
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=<your-project-id>
GOOGLE_CLOUD_LOCATION=us-central1
EOF
```

### Run Locally

```bash
cd ~
adk web
```

Open http://localhost:8000, select `zoo_guide_agent`, and ask:
> "Where can I find bears?"

---

## ☁️ Cloud Run Deployment

### Deploy MCP Server

```bash
cd mcp-on-cloudrun
gcloud run deploy coding-zoo-mcp-server \
    --no-allow-unauthenticated \
    --region=us-central1 \
    --source=. \
    --min=1
```

### Deploy ADK Agent

```bash
cd zoo_guide_agent
adk deploy cloud_run \
  --project=<your-project-id> \
  --region=us-central1 \
  --service_name=coding-zoo-tour-guide \
  --with_ui \
  .
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Agent Framework | Google ADK (Agent Development Kit) |
| LLM | Gemini 1.5 Flash via Vertex AI |
| MCP Server | FastMCP (Python) |
| Containerisation | Docker + Cloud Build |
| Hosting | Google Cloud Run |
| Auth | Google IAM + ID Token |

---

## 📁 Project Structure

```
.
├── Dockerfile                  # Root container image for the API
├── main.py                     # FastAPI wrapper for the agent
├── requirements.txt            # Python dependencies
├── README.md
├── zoo_guide_agent/
│   ├── agent.py               # ADK root_agent definition with MCPToolset
│   ├── requirements.txt       # Agent-specific dependencies
│   ├── Dockerfile             # ADK Cloud Run container
│   └── .env                   # Environment variables (not committed)
└── mcp-on-cloudrun/
    ├── server.py              # FastMCP zoo data server
    ├── local_mcp_call.py      # Local test script
    └── Dockerfile
```

---

## 💡 Example Queries

| Query | Expected Behaviour |
|---|---|
| "Where can I find bears?" | Returns zoo habitat location + bear species info |
| "Where can I find elephants?" | Combines MCP zoo data with conservation context |
| "Where can I find penguins?" | Uses `fetch_animals_by_species` MCP tool |
