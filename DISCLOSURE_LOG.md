# 📄 AI & Human Collaboration Disclosure Log

**Project Name:** TrendPulse (`vibewright`)  
**Hackathon Track:** Problem Statement #1 — RAG-Based Trend Automation Tool  
**Repository:** [github.com/piyush28verma/vibewright](https://github.com/piyush28verma/vibewright)  
**Date:** August 23, 2026  

---

## 💡 Executive Summary

TrendPulse was co-developed using an agentic pair-programming workflow between the human lead developer and an AI Coding Assistant. The project's vision, problem selection, architectural constraints, strict Swytchcode policy gating, multi-source ingestion requirements, and live platform posting decisions were **100% human-directed**. The AI was utilized for rapid code scaffolding, vector store indexing boilerplate, CSS design system generation, and API wrapper implementations.

---

## ⚖️ Collaboration & Decision Matrix

| Domain | Human Strategic Ownership | AI Technical Execution |
|---|---|---|
| **Problem Statement Selection** | Evaluated 3 hackathon problem statements; selected **Statement #1** (RAG Trend Automation) as the best alignment for Swytchcode execution layer. | Provided competitive comparative analysis and risk scoring across all 3 statements. |
| **Swytchcode Integration** | Rejected mock client wrappers; mandated **native `swytchcode-runtime` SDK** and official `swy` CLI `tooling.json` allowlist format. | Generated wrapper functions with automatic fallback logic when Swytchcode CLI isn't locally authenticated. |
| **Multi-Source Data Ingestion** | Enforced 5 distinct sources (**NewsAPI, Reddit, HackerNews, Dev.to, Google News RSS**) to satisfy "news, social chatter, and emerging topics". | Implemented RSS XML parsing, httpx async callers, and unified `TrendItem` normalization logic. |
| **Publishing Target** | Rejected dummy/mock POST endpoints; required **real Reddit posting (`r/test`)** via PRAW/Swytchcode to return a clickable URL for judges. | Handled PRAW script auth integration, error handling, and post permalink extraction. |
| **Tech Stack & Architecture** | Dictated FastAPI backend, ChromaDB vector store, Groq LLM (`llama-3.3-70b`), and React + Vite frontend with dark glassmorphism theme. | Built component scaffold (`PipelineVisualizer`, `RAGInspector`, `SwytchcodeLog`) and SSE streaming routes. |
| **Design System & UX** | Directed dark theme, neon accents, SSE step-by-step pulse animations, and real-time similarity score visualization. | Generated 450+ lines of custom glassmorphism CSS keyframes and reactive UI state bindings. |

---

## 💬 Prompt & Iteration Timeline

### Phase 1: Strategic Alignment & Problem Statement Analysis
- **Human Directive:** Provided the 3 hackathon problem statements and asked for competitive ranking to maximize win potential.
- **AI Output:** Ranked Statement 3 (Game) #1, Statement 2 #2, Statement 1 #3 based on raw visual demo factor.
- **Human Course Correction:** Informed AI that **Swytchcode integration is mandatory**. Prompted re-evaluation based on native platform fit.
- **Outcome:** Statement #1 elevated to #1 rank because Swytchcode natively serves as the execution layer for API trend fetching and social posting.

### Phase 2: Architecture & Guardrail Definition
- **Human Directive:** Demanded a 60-minute execution plan using FastAPI, Groq LLM, and ChromaDB vector RAG.
- **AI Initial Plan:** Suggested a mock `swytchcode_client.py` and a dummy `/api/mock/social-post` endpoint.
- **Human Strict Critique:** Flagged mock code as unacceptable for hackathon judging:
  > *"🔴 Critical: You're building a fake Swytchcode. Use `swytchcode-runtime` pip package and `swy` CLI. And the post must actually post somewhere real (Reddit/Discord), not a mock endpoint."*
- **Outcome:** Architecture revised to use native `swytchcode-runtime` SDK and PRAW posting to Reddit `r/test`.

### Phase 3: Multi-Source Trend Scope Expansion
- **Human Directive:** Noticed single/dual source reliance and insisted on rich multi-source coverage:
  > *"Why are you using a single source? Use as many sources as required by the PS — news, social chatter, emerging topics."*
- **AI Output:** Expanded `trend_fetcher.py` to ingest 5 live feeds simultaneously (NewsAPI, Reddit, HackerNews, Dev.to, Google News RSS) into ChromaDB.

### Phase 4: Frontend & Deployment
- **Human Directive:** Specified React + Vite dashboard structure, dark glassmorphism styling, and requested creation of GitHub repository `vibewright` under account `piyush28verma`.
- **AI Execution:** Built React components, SSE listener, `.gitignore`, `README.md`, committed code, and pushed main branch via `gh repo create`.

---

## 🛡️ Integrity & Verification

1. **Non-Hallucination Guarantee:** Grounding prompt ensures the LLM generates posts using *only* retrieved vector passages from ChromaDB with explicit `[1], [2]` citation badges.
2. **Security & Secrets:** All API keys (`GROQ_API_KEY`, `NEWSAPI_KEY`, `REDDIT_CLIENT_SECRET`) are isolated in `.env` and strictly excluded from Git tracking via `.gitignore`.
3. **Open Source Compliance:** All third-party libraries (FastAPI, ChromaDB, SentenceTransformers, React, Vite) are used under standard MIT/Apache-2.0 open-source licenses.

---

*Submitted by the TrendPulse (`vibewright`) Hackathon Team.*
