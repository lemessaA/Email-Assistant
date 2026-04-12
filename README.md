# ✉️ Email Assistant AI

<p align="center">
  <em>A production-grade, Agentic AI-powered email assistant to manage, draft, and review communications with human-in-the-loop capabilities.</em>
</p>

---

## 🚀 Features

- **🧠 Agentic Workflows:** Powered by LangGraph and state-of-the-art LLMs to draft, summarize, and categorize your emails.
- **🛡️ Guardrails & Safety:** Built-in safeguards to ensure professional and compliant email communications.
- **👥 Human-in-the-Loop (HITL):** Configurable review checkpoints allowing human approval before high-risk emails are sent.
- **📮 Full Email Integration:** Seamless support for both IMAP (to read incoming emails) and SMTP (to send outgoing responses directly).
- **📊 Real-time Evaluations:** Built-in evaluation framework to verify the quality and correctness of AI-generated drafts.
- **🎨 Modern Next.js Frontend:** A high-performance, premium Next.js frontend with dark-mode styling for an optimal user experience.
- **⚡ Fast & Scalable Backend:** Asynchronous FastAPI backend offering a robust and typed API.

## 🛠️ Tech Stack

**Frontend:**
- [Next.js 15](https://nextjs.org/) (App Directory)
- React
- Tailwind CSS (Premium Dark Mode UI)

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) (Python)
- [LangGraph](https://python.langchain.com/docs/langgraph) & [LangChain](https://python.langchain.com/)
- SQLite + SQLite Vector Store (ChromaDB)
- SMTP / IMAP Integrations

## 📂 Project Structure

```
Email-Assistant/
├── app.py                    # FastAPI / Vercel entrypoint
├── langgraph.json            # LangGraph graph configuration
├── pyproject.toml            # Project metadata & dependencies
├── uv.lock                   # Dependency lock file
├── .env.example              # Environment variable template
│
├── src/                      # Backend source code
│   ├── agents/               # LangGraph agent, tools & workflow
│   ├── api/                  # FastAPI app, schemas & routes
│   ├── core/                 # Config, LLM, embeddings & memory
│   ├── database/             # SQLite models, CRUD & connection
│   ├── eval/                 # Evaluation framework & metrics
│   ├── guardrails/           # Content safety validation
│   ├── hitl/                 # Human-in-the-Loop review manager
│   ├── integrations/         # Google Calendar & Web Search
│   ├── services/             # Email sender (SMTP)
│   └── utils/                # Logging, parsing & templates
│
├── frontend/                 # Next.js 15 frontend
│   └── src/
│       ├── app/              # App Router pages (settings, etc.)
│       ├── components/       # UI components (features + layout)
│       ├── types/            # TypeScript type definitions
│       └── utils/            # API client & helpers
│
├── deploy/                   # All deployment configuration
│   ├── docker/               # Dockerfile, Dockerfile.ui, docker-compose.yml
│   ├── nginx/                # nginx.conf (reverse proxy)
│   ├── monitoring/           # Prometheus config
│   ├── render.yaml           # Render.com service config
│   ├── deploy.sh             # Generic deploy script
│   ├── deploy-render.sh      # Render-specific deploy script
│   ├── docker-deploy.sh      # Docker deploy script
│   └── deploy.py             # Python deploy helper
│
├── docs/                     # Project documentation
│   ├── DEPLOYMENT.md
│   ├── DOCKER.md
│   ├── GOOGLE_CALENDAR_SETUP.md
│   ├── RENDER_DEPLOYMENT.md
│   └── WEB_SEARCH_SETUP.md
│
├── tests/                    # Test suite
│   ├── test_email.py
│   ├── test_guardrails.py
│   ├── test_hitl.py
│   └── test_real_emails.py
│
└── data/                     # Runtime data & email drafts
    └── drafts/
```

## ⚙️ Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- An active Email Account that supports IMAP/SMTP (e.g., Gmail with App Passwords)

## 💻 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/lemessaA/Email-Assistant.git
cd Email-Assistant
```

### 2. Backend Setup

Set up a virtual environment and load dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

Configure your environment variables by copying the template:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```ini
# LLM Provider Configuration
GROQ_API_KEY="your_groq_api_key_here"

# SMTP Configuration (For Sending Emails)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="your.email@gmail.com"
SMTP_PASSWORD="your-app-password"

# IMAP Configuration (For Receiving Emails)
IMAP_SERVER="imap.gmail.com"
IMAP_PORT=993
EMAIL_USER="your.email@gmail.com"
EMAIL_PASSWORD="your-app-password"
```

Start the FastAPI development server:

```bash
uvicorn app:app --reload
```
The API should now be running locally at **http://localhost:8000** 🚀

### 3. Frontend Setup

In a new terminal window, navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The Next.js UI should now be available at **http://localhost:3000** ✨

## 🐳 Docker Support

This application can also be deployed seamlessly via Docker. For specialized instructions regarding Docker, refer to [`docs/DOCKER.md`](docs/DOCKER.md).

## 📝 License

This project is open-source and available under the standard MIT License.