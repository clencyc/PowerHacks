# SafeSpace AI - GBV Detection & Reporting System 🛡️

A comprehensive Gender-Based Violence (GBV) detection and reporting system built for Slack workspaces, with a focus on Kenyan workplace safety and legal compliance.

## ✨ MVP Features (Ready to Ship)

### 🤖 Real-Time GBV Detection
- **AI-Powered Analysis**: Uses HuggingFace Toxic-BERT for toxicity detection
- **GBV-Specific Patterns**: Harassment, discrimination, threats, sexual content
- **Swahili Support**: Kenyan workplace context and language patterns
- **Smart Severity**: High/Medium/Low classification with context awareness

### 📱 Production-Ready Slack Bot
- **Proactive Monitoring**: Scans all messages in real-time
- **Private Intervention**: Sends help privately, never publicly shames
- **Slash Commands**: `/gbv-help`, `/gbv-report`, `/gbv-privacy`
- **Anonymous Reports**: Encrypted, zero-knowledge reporting system

### 🇰🇪 Kenyan Legal & Resource Integration
- **24/7 Hotlines**: Gender Violence Recovery Centre (0709 558 000)
- **Legal Framework**: Sexual Offences Act, Employment Act guidance
- **Local NGOs**: FIDA Kenya, Childline Kenya integration
- **Workplace Rights**: Kenya-specific employment law guidance

## 🚀 Quick Start (Ship Today!)

### 1. Get Your Slack Tokens
1. Go to [Slack API](https://api.slack.com/apps) → Create New App
2. Copy these tokens to your `.env`:
   - Bot User OAuth Token (`SLACK_BOT_TOKEN`)
   - App-Level Token (`SLACK_APP_TOKEN`) 
   - Signing Secret (`SLACK_SIGNING_SECRET`)

### 2. One-Command Setup
```bash
git clone https://github.com/clencyc/PowerHacks
cd PowerHacks
./setup.sh  # Creates .env, generates encryption keys
```

### 3. Configure Slack App
**Bot Token Scopes (Required):**
```
channels:history, groups:history, im:history
chat:write, chat:write.public, commands
users:read, app_mentions:read
```

**Event Subscriptions (Required):**
```
message.channels, message.im, message.groups, app_mention
```

**Slash Commands (Add these):**
- `/gbv-help` - Get help and resources
- `/gbv-report` - Anonymous reporting  
- `/gbv-privacy` - Privacy policy

### 4. Launch MVP
```bash
# Start all services
docker-compose up -d

# Your bot is now live! 🚀
# API running at: http://localhost:8000
# Bot monitoring all Slack channels
```

## 🏗️ Project Structure

```
PowerHacks/
├── apps/
│   ├── api/           # FastAPI Backend with GBV detection API
│   │   ├── main.py    # Enhanced with detection, reports, analytics
│   │   ├── models.py  # Complete data models for reports & analytics
│   │   ├── routers/   # API endpoints for all features
│   │   └── Dockerfile # Production-ready container
│   └── slack/         # Production Slack Bot
│       ├── app.py     # Complete bot with all GBV features  
│       ├── detection.py # HuggingFace Toxic-BERT + GBV patterns
│       ├── rag.py     # Kenyan legal resources & hotlines
│       └── Dockerfile # Container with ML dependencies
├── docker-compose.yml # Full production setup
├── setup.sh          # One-command setup script
└── .env.example      # All required environment variables
```

## 🤖 How It Works

### Real-Time Detection
1. **Message Monitoring**: Bot listens to all channels it's invited to
2. **AI Analysis**: Every message → Toxic-BERT + GBV pattern matching  
3. **Smart Response**: High severity → immediate DM with resources
4. **Anonymous Reporting**: `/gbv-report` opens encrypted reporting modal

### Kenyan Context Integration
- **Legal Resources**: Constitution Article 27, Sexual Offences Act 2006
- **Emergency Hotlines**: Gender Violence Recovery Centre (0709 558 000)
- **Swahili Detection**: "msichana", "mwanamke", harassment patterns
- **Workplace Rights**: Employment Act Section 6 guidance

## 📊 Admin Dashboard Features

### Real-Time Analytics
```http
GET /api/v1/reports/stats/dashboard
```
Returns:
- Total reports & pending count
- High-severity incident alerts
- Weekly trends & resolution rates
- Top categories (harassment, discrimination, etc.)

### Report Management
```http
# List all reports with filters
GET /api/v1/reports/?status=pending&severity=high

# Update report status
PATCH /api/v1/reports/123
{
  "status": "resolved", 
  "review_notes": "Handled by HR team"
}
```

## 🔒 Privacy & Security (GDPR Compliant)

### What We Encrypt
- ✅ All incident reports (Fernet encryption)
- ✅ User identities in reports (anonymous)  
- ✅ Audit logs for admin actions

### What We DON'T Store
- ❌ Full message content (unless flagged)
- ❌ Private conversations
- ❌ Personal identifying information

### Data Retention
- Message metadata: 30 days max
- Reports: Until resolved, then archived
- Auto-deletion: Configurable via environment

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
