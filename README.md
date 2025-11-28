# SafeSpace AI

An AI-powered plugin that detects and prevents Gender-Based Violence and harassment in workplace collaboration tools.

## Repository
[https://github.com/clencyc/PowerHacks](https://github.com/clencyc/PowerHacks)

## Project Structure
This is a monorepo managed by [Turborepo](https://turbo.build/).

- `apps/api`: FastAPI Backend (Python)
- `apps/slack`: Slack Bot (Bolt for Python)
- `apps/web`: Admin Dashboard (Next.js)
- `packages/shared`: Shared utilities

## Setup

### Prerequisites
- Node.js >= 18
- Python >= 3.12
- Docker (for local DB/Qdrant)
- pnpm

### Installation
```bash
pnpm install
```

### Development
```bash
pnpm dev
```

## Deployment
See `docs/deployment.md` for details.
