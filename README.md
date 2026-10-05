# REPO_MONITORING_AGENT

A background AI agent that monitors a GitHub repository and autonomously triages issues, drafts PR descriptions, and generates weekly health reports — using a multi-step LLM reasoning loop with persistent memory.

## Architecture

```
GitHub Webhook (issue / PR event)
        ↓
FastAPI webhook receiver (local, ngrok tunnel for dev)
        ↓
Agent Orchestrator (Python)
        ├── Step 1: Parse event payload
        ├── Step 2: LLM Call 1 — Classify intent
        │           Input: issue title + body
        │           Output: { type: bug|feature|question, priority: high|med|low, summary: str }
        ├── Step 3: Tool selection — which action to take
        │           Tools: [apply_label, post_comment, assign_user, flag_duplicate]
        ├── Step 4: Execute tool (GitHub API call)
        ├── Step 5: LLM Call 2 — Reflect on result, draft comment
        │           Input: action taken + issue context
        │           Output: structured comment text
        └── Step 6: Post comment to GitHub issue

Persistent Memory (ChromaDB)
        ← stores past triage decisions
        → retrieved at Step 2 for similar-issue context

State Store (SQLite)
        ← logs every agent run (input, decision, action, output, timestamp)
```

**System design concept in play:** event-driven architecture. The agent is stateless between runs — it receives an event, processes it, terminates. State lives in ChromaDB + SQLite, not in memory. Same pattern as AWS Lambda + DynamoDB.

## Tech stack

| Component | Choice | Why |
|---|---|---|
| Language | Python | LLM ecosystem is Python-first |
| LLM | Groq (hosted, `openai/gpt-oss-120b`) **or** Ollama (local) — pluggable via `LLM_PROVIDER` | Groq: free tier, fastest hosted inference, no card (Llama 3.3 70B was free-tier but moved to Enterprise-only in 2026 — gpt-oss-120b is the current free-tier equivalent). Ollama: fully offline fallback, no key, bounded by local hardware |
| Webhook receiver | FastAPI | Async, lightweight, OpenAPI docs auto-generated |
| GitHub integration | PyGithub | Official Python SDK |
| Vector memory | ChromaDB | Local, no server needed, free |
| State / logs | SQLite | Zero-config, persistent, queryable |
| Embeddings | Google Gemini text-embedding-004 | Free via AI Studio |
| Dev tunnel | ngrok (free tier) | Exposes localhost to GitHub webhook |

See `SCOPE.md` for what this agent does and does not do.
