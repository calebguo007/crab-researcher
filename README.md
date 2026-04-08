# CrabRes

> CrabRes is a growth agent I built for indie developers. It works, but not well enough yet — and that gap taught me more about agent design than anything else.

> An AI growth strategy agent for indie developers — not just chat, but an agent that actually does the research, shapes the strategy, ships the content, and watches the competition.

---

## What is this

**CrabRes** is a growth agent that lives in your terminal and browser. Hand it your product, and it will:

1. **Research proactively** — searches for competitors, scrapes landing pages, and reads social media on its own. It won't bombard you with questions before doing any work.
2. **A 13-expert roundtable** — Market Researcher, Economist, Content Strategist, Social Media Expert, Paid Ads, Partnerships, AI Distribution, Consumer Psychologist, Product Growth, Data Analyst, Master Copywriter, Strategy Critic, and Design Expert — dynamically weighted by product type.
3. **Continuous watch** — Growth Daemon runs every 30 minutes: scans competitor changes, captures social mentions, and tracks how the content you shipped is performing.
4. **Dreams every night** — Growth Dream runs at midnight, distilling the day's scattered signals into long-term memory. It wakes up understanding your product a little better each day.
5. **Actually takes action** — not just suggestions. It posts to X via the API, drafts directory submissions, and writes outreach emails.

Core principle: **Research First, Ask Last**. The agent's default action is to search, not to interrogate.

---

## Why I built this

What indie developers lack isn't product chops — it's growth chops. Most "AI marketing tools" on the market are ChatGPT wrappers with templates: ask a question, get an answer. No real research chain, no memory, no autonomous action.

CrabRes is an attempt at an **agent that actually touches the real world**:
- It can **see** (Playwright screenshots + multimodal understanding)
- It can **search** (Tavily deep search + Firecrawl deep scrape)
- It can **publish** (X API v2 with OAuth 1.0a)
- It can **remember** (8 memory categories + vector retrieval)
- It can **think** (4-tier LLM routing — strong models for critical decisions, cheap models for parsing)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                  │
│  React + Tailwind + Zustand                         │
│  Expert roundtable chat / Growth dashboard / Memory │
└──────────────────┬──────────────────────────────────┘
                   │ SSE streaming + REST
┌──────────────────▼──────────────────────────────────┐
│  Backend (Render)                                   │
│  FastAPI + SQLAlchemy + asyncio                     │
│                                                     │
│  ┌─────────────────────────────────────────┐        │
│  │  Agent Engine                           │        │
│  │  ├─ ReAct Loop (think→act→observe)      │        │
│  │  ├─ Pipeline Runner (Coordinator)       │        │
│  │  ├─ Expert Pool (13, weighted)          │        │
│  │  ├─ Tool Registry                       │        │
│  │  └─ Memory (8 categories + pgvector)    │        │
│  └─────────────────────────────────────────┘        │
│                                                     │
│  ┌─────────────────────────────────────────┐        │
│  │  Growth Daemon (30-min tick)            │        │
│  │  competitors → social → campaigns → push│        │
│  └─────────────────────────────────────────┘        │
│                                                     │
│  ┌─────────────────────────────────────────┐        │
│  │  Growth Dream (midnight distillation)   │        │
│  │  orient → gather → consolidate → prune  │        │
│  └─────────────────────────────────────────┘        │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┼─────────┬──────────┬──────────┐
         ▼         ▼         ▼          ▼          ▼
      Moonshot  OpenRouter  Tavily  Firecrawl   Neon
      (critical) (vision)  (search) (deep scrape) (PG+pgvector)
```

---

## Core Features

### 1. A Research-First Agent Loop
The Coordinator's first rule is simple: **if you can search, don't ask.** When a user sends a terse message like "xx is a competitor", the agent immediately:
- Fires `web_search("xx competitor analysis")`
- Scrapes the top result's landing page
- Extracts product info and writes it to memory
- Only then replies — it does not open with "can you tell me more?"

### 2. The 13-Expert Roundtable
Not a simple prompt swap — experts are dynamically weighted by product type (SaaS / tool / community / content). A B2B SaaS surfaces the Economist and Partnerships experts; a consumer tool surfaces Social Media and Psychologist. Every expert has its own thinking style and knowledge base.

### 3. Growth Daemon — Real Background Work
Not a cron job — a continuously running loop:
- **Competitor scan**: reads `research/competitors.json`, diffs each competitor's landing page, pushes alerts on pricing changes or new features
- **Social scan**: searches for mentions of your product and every tracked competitor on X / Reddit / HN
- **Campaign tracking**: if an `active_campaign` is set (e.g. a tweet URL), pulls engagement hourly
- **Discovery push**: new findings land in `pending_discoveries`; the frontend polls and surfaces them

### 4. Automatic Competitor Discovery & Tracking
Search results are auto-filtered (twitter / reddit / search-engine domains are dropped), extracted competitor domains are written to `research/competitors.json`, and the Daemon starts tracking them automatically. Users never have to type a competitor list by hand.

### 5. It Can See and Ship
- **BrowseWebsiteTool**: real browser via Playwright + screenshot, then Gemini 2.0 Flash or GPT-4o-mini reads the image and returns product positioning / value prop / pricing / trust signals / design style
- **TwitterPostTool**: real tweet publishing with OAuth 1.0a signing — not "here's the draft, copy-paste it yourself"

### 6. Memory System
Eight categorized directories plus pgvector semantic search:
```
.crabres/memory/{user_id}/
├── product/      # product essence
├── goals/        # goals & OKRs
├── research/     # competitors, market data
├── strategy/     # strategic decisions
├── execution/    # actions taken
├── feedback/     # outcome signals
├── journal/      # conversation logs
└── knowledge/    # long-term knowledge
```

### 7. Trust Levels
Cautious → Building → Trusted → Autopilot. Early on, the agent confirms every action. As trust grows, it can autonomously post, reach out, and hit external systems on the user's behalf.

### 8. Four-Tier LLM Routing
- **CRITICAL**: strategic decisions — Claude Opus / Moonshot K2
- **THINKING**: expert reasoning — Moonshot v1-32k
- **WRITING**: copy generation — DeepSeek / Qwen
- **PARSING**: structured extraction — GPT-4o-mini / Gemini Flash

Saves money without cutting corners on the decisions that matter.

---

## Tech Stack

**Backend**
- FastAPI + Pydantic v2 + SQLAlchemy 2.0 async
- PostgreSQL (Neon) + pgvector
- Playwright (browser) + httpx (HTTP)
- Moonshot / OpenRouter / OpenAI multi-LLM routing
- Tavily (search) + Firecrawl (deep scrape)
- Tweepy / hand-rolled OAuth 1.0a

**Frontend**
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- Zustand (state) + SSE (streaming chat)

**Deployment**
- Frontend: Vercel
- Backend: Render (Web Service + Background Worker for Daemon)
- Database: Neon PostgreSQL

---

## Quick Start

Live at: https://crab-researcher.vercel.app/

Multiple entry points: web frontend, Discord / WhatsApp / Feishu bindings, CLI, and MCP plugin.

---

## Project Structure

```
crab-researcher/
├── app/
│   ├── agent/
│   │   ├── engine/          # ReAct loop / pipeline / LLM adapter
│   │   ├── experts/         # 13 expert implementations
│   │   ├── tools/           # research / action / browser / twitter tools
│   │   ├── daemon/          # Growth Daemon
│   │   ├── dream/           # Growth Dream memory distillation
│   │   └── memory/          # 8-category memory system
│   ├── api/v2/              # REST + SSE endpoints
│   ├── core/                # config, security, database
│   └── models/              # SQLAlchemy models
├── frontend/                # React frontend
├── alembic/                 # database migrations
├── docs/planning/           # Chinese planning & research docs
└── tests/                   # pytest
```

---

## Design Philosophy

> "An agent that only asks questions isn't an agent — it's a questionnaire."

Every design decision in CrabRes answers the same question: **does this make the agent feel more like a real growth partner, or more like a chatbot?**

- Search over asking
- Action over advice
- Memory over context
- Multiple expert perspectives over a single answer
- Continuous monitoring over one-shot consulting

---

## Roadmap

**Now (P0)**: connect the agent to the real world
- [x] Research-First loop rewrite
- [x] Automatic competitor discovery & tracking
- [x] X/Twitter API publishing
- [x] Multimodal screenshot understanding
- [ ] Daemon feedback loop (campaign outcomes → expert learning)
- [ ] MCP client (plug in the user's own tools)

**Next**: memory and trust
- [ ] Trust Levels frontend UI
- [ ] Growth Dream long-term insight visualization
- [ ] Expert weights evolving with product type

---

## License

MIT

---

**CrabRes — not just advice, action.**
