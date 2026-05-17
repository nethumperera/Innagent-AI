# 🏨 InnAgent AI

**Multi-Agent AI Hotel Management Platform for Co Host Ceylon**

> Built for NIBM NeoVentures 2026 — Prototype v1.0

InnAgent AI is an autonomous hotel management assistant built exclusively for [Co Host Ceylon](https://www.cohostceylon.com) — a boutique hospitality management company in Sri Lanka managing OTA listings, reservations, and guest experience for small and mid-level hotels and villas.

## Architecture

```
┌──────────────┐    ┌──────────────────────────────────┐
│  Next.js 14  │    │       FastAPI Backend             │
│  Dashboard   │───▶│  ┌──────────────────────────────┐ │
│  (Port 3000) │    │  │   LangGraph Orchestrator     │ │
└──────────────┘    │  │  ┌──────┐ ┌──────┐ ┌──────┐ │ │
                    │  │  │Price │ │Guest │ │Rev.  │ │ │
┌──────────────┐    │  │  │Agent │ │Bot   │ │Agent │ │ │
│  WhatsApp    │───▶│  │  └──────┘ └──────┘ └──────┘ │ │
│  (Twilio)    │    │  │  ┌──────┐ ┌──────┐          │ │
└──────────────┘    │  │  │Review│ │Ops   │          │ │
                    │  │  │Agent │ │Agent │          │ │
┌──────────────┐    │  │  └──────┘ └──────┘          │ │
│ GitHub Cron  │───▶│  └──────────────────────────────┘ │
└──────────────┘    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │     Supabase (PostgreSQL)         │
                    └────────────────┬─────────────────┘
                                     │
                    ┌────────────────▼─────────────────┐
                    │      Groq API (LLaMA 3.3 70B)    │
                    └──────────────────────────────────┘
```

## 5 AI Agents

| Agent | Purpose | Trigger |
|-------|---------|---------|
| **PricingAgent** | Dynamic room pricing with peak season multipliers | Daily 6AM IST / Manual |
| **GuestBot** | Multilingual guest communication (EN/SI/TA) | WhatsApp webhook |
| **RevenueAgent** | KPI calculation (RevPAR, ADR, Occupancy) | Dashboard / Manual |
| **ReviewAgent** | Review response drafting (never auto-posts) | Daily 9AM IST / Manual |
| **OperationsAgent** | Housekeeping & maintenance task management | Daily 7AM IST / Manual |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Supabase project (free at [supabase.com](https://supabase.com))

### 1. Clone & Configure

```bash
git clone https://github.com/nethumperera/Innagent-AI.git
cd Innagent-AI

# Copy environment files
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local

# Edit .env with your API keys
```

### 2. Database Setup

Run `database/schema.sql` in your Supabase SQL editor to create all tables, indexes, RLS policies, and seed data.

### 3. Backend

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the dashboard works with demo data even without API keys.

## API Endpoints

### Hotels
```bash
# List all hotels
curl http://localhost:8000/hotels/

# Get hotel profile
curl http://localhost:8000/hotels/{hotel_id}

# Create hotel
curl -X POST http://localhost:8000/hotels/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Hotel", "slug": "my-hotel", "total_rooms": 10}'
```

### Agent
```bash
# Run pricing check
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "daily_pricing_check", "hotel_id": "your-hotel-id"}'

# Run guest bot
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "guest_message", "hotel_id": "your-hotel-id", "context": {"guest_message": "Do you have rooms for Dec 25?"}}'
```

### Dashboard
```bash
# Get dashboard summary
curl http://localhost:8000/dashboard/summary/{hotel_id}

# Get metrics (7-day)
curl http://localhost:8000/dashboard/metrics/{hotel_id}?days=7

# Get recent activity
curl http://localhost:8000/dashboard/activity?limit=10
```

### Reviews
```bash
# List reviews
curl http://localhost:8000/reviews/{hotel_id}

# Approve a review response
curl -X POST http://localhost:8000/reviews/action \
  -H "Content-Type: application/json" \
  -d '{"review_id": "review-uuid", "action": "approve"}'
```

### WhatsApp Webhook
```bash
# Test locally with ngrok
ngrok http 8000
# Set Twilio webhook URL to: https://your-ngrok-url/webhook/whatsapp
```

## Adding a New Hotel

1. **Supabase**: Insert into `hotels` table with all required fields
2. **Rooms**: Insert room types into `rooms` table with `hotel_id` reference
3. **WhatsApp**: Set the hotel's `whatsapp_number` field to map incoming messages
4. **Dashboard**: Hotel appears automatically in the hotel selector dropdown

## Testing WhatsApp Locally

1. Install [ngrok](https://ngrok.com): `npm install -g ngrok`
2. Start backend: `uvicorn backend.main:app --port 8000`
3. Start tunnel: `ngrok http 8000`
4. Copy the ngrok HTTPS URL
5. In Twilio Console → WhatsApp Sandbox → set webhook to `https://your-url/webhook/whatsapp`
6. Send a WhatsApp message to the Twilio sandbox number

## Free Tier Limits

| Service | Free Tier | Limit |
|---------|-----------|-------|
| **Groq** | Free | 14,400 req/day, 6,000 tokens/min |
| **Supabase** | Free | 500MB DB, 1GB storage, 50K auth users |
| **Twilio** | Sandbox | WhatsApp sandbox (verified numbers only) |
| **Railway** | Free Trial | $5 credit, 500 hours/month |
| **Vercel** | Hobby | 100GB bandwidth, serverless functions |
| **GitHub Actions** | Free | 2,000 min/month |

## Deployment

### Backend → Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Set all `.env` variables in Railway dashboard.

### Frontend → Vercel

```bash
cd frontend
npx vercel
```

Set `NEXT_PUBLIC_API_URL` to your Railway backend URL.

## Tech Stack

- **Backend**: FastAPI, LangGraph, Groq (LLaMA-3.3-70B), Supabase, Twilio
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Recharts, Lucide
- **Database**: PostgreSQL (Supabase) with RLS
- **AI**: 5 specialized agents with LangGraph orchestration
- **CI/CD**: GitHub Actions cron jobs

---

**InnAgent AI** — Managed by [Co Host Ceylon](https://www.cohostceylon.com) | NIBM NeoVentures 2026
