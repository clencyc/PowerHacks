# Deployment Guide

## Prerequisites

- Railway or Fly.io account
- OpenAI/Anthropic API Keys
- Slack App Credentials
- Perspective API Key

## Steps

### 1. Database & Vector DB

- Provision a PostgreSQL instance.
- Provision a Qdrant instance (or use Qdrant Cloud).

### 2. Backend API

- Deploy `apps/api` as a Python service.
- Set Environment Variables:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `PRIVATE_KEY_PATH` (or content)

### 3. Slack Bot

- Deploy `apps/slack` as a Python service.
- Set Environment Variables:
  - `SLACK_BOT_TOKEN`
  - `SLACK_APP_TOKEN`
  - `OPENAI_API_KEY`
  - `QDRANT_URL`
  - `PERSPECTIVE_API_KEY`

### 4. Admin Dashboard

- Deploy `apps/web` to Vercel or Railway.
- Set Environment Variables:
  - `NEXT_PUBLIC_API_URL`

## Railway Deployment (Recommended)

Railway is the easiest way to deploy this monorepo.

### 1. Setup Project

1. Login to [Railway](https://railway.app/).
2. Click **"New Project"** -> **"Deploy from GitHub repo"**.
3. Select your `safespace-ai` repository.

### 2. Configure Services

Railway will try to detect the services. You might need to add them manually or configure the "Root Directory" for each.

#### **Service A: Database (PostgreSQL)**

1. Right-click the canvas -> **Add Service** -> **Database** -> **PostgreSQL**.
2. Wait for it to initialize.

#### **Service B: Backend API**

1. Add a service connected to your repo.
2. **Settings** -> **Root Directory**: `apps/api`
3. **Variables**:
    - `DATABASE_URL`: Reference the Postgres service (type `${{Postgres.DATABASE_URL}}`).
    - `SECRET_KEY`: Generate a random string.
    - `PRIVATE_KEY_PATH`: `/app/private_key.pem` (You may need to generate this key and add it as a file or variable).

#### **Service C: Slack Bot**

1. Add a service connected to your repo.
2. **Settings** -> **Root Directory**: `apps/slack`
3. **Variables**:
    - `SLACK_BOT_TOKEN`: Your Bot User OAuth Token (`xoxb-...`).
    - `SLACK_APP_TOKEN`: Your App-Level Token (`xapp-...`).
    - `OPENAI_API_KEY`: Your OpenAI Key.
    - `PERSPECTIVE_API_KEY`: Your Google Perspective API Key.

#### **Service D: Admin Dashboard**

1. Add a service connected to your repo.
2. **Settings** -> **Root Directory**: `apps/web`
3. **Build Command**: `pnpm build`
4. **Start Command**: `pnpm start`
5. **Variables**:
    - `NEXT_PUBLIC_API_URL`: The public URL of your **Backend API** service (e.g., `https://api-production.up.railway.app`).

### 3. Finalize

1. Click **Deploy** on each service.
2. Once the **Slack Bot** is running, update your Slack App configuration (Manifest) to point to the new URL if you are using HTTP endpoints (though this bot uses Socket Mode, so no URL config needed!).
