# SafeSpace AI Architecture

## Overview
SafeSpace AI is a modular system designed to detect and prevent harassment in Slack.

## Components

### 1. Slack Bot (Python/Bolt)
- **Responsibility**: Real-time message interception, toxicity detection, user interaction (modals, commands).
- **Integration**: Perspective API, HuggingFace, Backend API.

### 2. Backend API (FastAPI)
- **Responsibility**: Data persistence, encryption management, analytics aggregation.
- **Database**: PostgreSQL (via SQLModel).
- **Security**: RSA+AES hybrid encryption for reports.

### 3. RAG Engine (LangChain)
- **Responsibility**: Context-aware retrieval of policies and laws.
- **Vector DB**: Qdrant.
- **LLM**: GPT-4o-mini / Claude 3.5 Sonnet.

### 4. Admin Dashboard (Next.js)
- **Responsibility**: Analytics visualization, settings management.
- **UI**: Tailwind + Shadcn/UI.

## Data Flow
1. User sends message -> Slack Bot intercepts.
2. Bot calls Perspective API -> If toxic, sends ephemeral warning.
3. User reports incident -> Bot opens modal -> Encrypts data client-side -> Sends blob to API.
4. API stores blob in Postgres.
5. Admin views dashboard -> API aggregates anonymized stats -> Dashboard renders charts.
