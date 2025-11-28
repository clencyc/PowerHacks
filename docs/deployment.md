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

## One-Click Deploy (Railway)
*(Coming Soon)*
