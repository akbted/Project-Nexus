WorkAI — Ambient Agentic System Plan
1. Goal
A hierarchical, ambient agentic system over an OpenProject-backed MCP server. Answers questions on demand, and on schedules/events autonomously computes project/work/people insights that populate a frontend dashboards. No human prompt required for scheduled runs.
2. Verified facts (reality check)
- MCP server exists externally at ~/Desktop/Development/Rough Practice/MCP/ClientServer — 17 tools + 6 resources + 5 prompts, stdio transport, kept as-is (dumb capability layer). WorkAI spawns it via langchain-mcp-adapters; we never modify it.
- This folder (OpenProject MCP/) = WorkAI client/agent layer. Server and client are separate projects.
- OpenProject runs elsewhere — OPENPROJECT_APIROOT/OPENPROJECT_TOKEN must point at the remote host.
- Framework: from langchain.agents import create_agent (current API, create_react_agent deprecated). HITL via HumanInTheLoopMiddleware. Supervisors = subagents wrapped as @tool, not hand-coded nodes. langgraph-supervisor is no longer maintained — not used.
- LLM gateway = LiteLLM (in-process Router first; proxy container in the compose is optional/present).
3. Architecture (SOLID, beginner-friendly)
OpenProject (remote, :8080)
   │  HTTP /api/v3
[ MCP server (external, stdio) ]   ← dumb capability layer, unchanged
   │  langchain-mcp-adapters
[ WorkAI Orchestrator → StateGraph ]  ← only hand-built graph
   │  structured routing + RBAC + approval decision
   ▼
[ Supervisor = ONE create_agent ]  ← generic, bound to hierarchy.py entry
   │  specialists = wrapped tools (NOT separate agents)
   ▼
[ Insight store / API / ambient runner / HITL / Postgres + Redis + Qdrant ]
SOLID mapping: S = one job per module; O/L/D = everything behind Protocols (get_llm(), MemoryStore, GuardrailFilter, InsightStore) injected in factories.py; I = memory/insights/checkpointer are separate interfaces.
4. Docker services — final compose
User's compose (setup/open-project-docker.yml) with fixes:
- workai-db (postgres:16-alpine, :5432) ✓
- redis (redis:7-alpine, :6379) ✓
- qdrant (qdrant/qdrant, :6333/:6334) — fix: remove healthcheck (bash/curl absent in image)
- litellm (ghcr.io/berriai/litellm, :4000) — verify tag (v1.99.1 or main-latest); needs ./litellm_config.yaml at repo root
- pgadmin (:5050), redisinsight (:5540) ✓
- remove unused mem0-data volume
- deferred (add as profiles): ollama (LiteLLM fallback), openshell-gateway (Phase 7 isolation)
5. LLM gateway (agent/llm_config.yaml + llm.py)
model_list:
  - model_name: default
    litellm_params: { model: "openrouter/<model>", api_key: os.environ/OPENROUTER_API_KEY }
  - model_name: local
    litellm_params: { model: "ollama/<model>", api_base: "http://localhost:11434" }
litellm_settings:
  fallbacks: [{ "default": ["local"] }]
  num_retries: 2
get_llm() returns a ChatLiteLLM over the Router. All supervisors share it. Adding providers = editing config, not code.
6. Agent roster
- L0 Orchestrator — intent, routing, RBAC, synthesis (drives every run)
- L1 Project & Work Supervisor — 13 read tools (list_project, get_project, get_project_workpackages, get_project_summary, get_project_blockers, get_project_activities, get_project_members, get_work_package, get_work_package_hierarchy, get_work_package_activity, get_work_package_dependencies, get_statuses, get_assignee_workload)
- L1 Insights Supervisor — 6 tools + 4 skills (MorningStandup, ProjectHealthCheck, WeeklyTeamReview, EscalationReview) → writes insight records (frontend populates w/o humans)
- L1 People & Team — Phase 2
- L1 Admin (write) — Phase 2, always HITL, runs in OpenShell sandbox
- L1 Knowledge/RAG — Phase 2, Qdrant
All declared in hierarchy.py + schedules.yaml — scaling = adding a dict.
7. Persistence
- Postgres (workai-db): users_profiles, supervisors, schedules, runs, insights (index (project_id, is_new, created_at)), approvals, webhook_events, threads. LangGraph checkpointer = AsyncPostgresSaver (own tables) + AsyncPostgresStore. LiteLLM writes its own LiteLLM_* tables into the same DB (fine for dev).
- Redis: exact + semantic cache, lock:job:{id}, debounce:{project}:{event}, insights:recent:{project_id}, rate limits.
- Qdrant (Phase 2): workai_knowledge, workai_mem0, workai_insight_archive.
8. Caching strategy
1. Provider prompt caching — stable supervisor prefix (system prompt + tools), static-before-variable ordering; Anthropic AnthropicPromptCachingMiddleware(type="ephemeral", ttl="1h")
2. Redis RedisSemanticCache — recurring deterministic lookups; never cache write tools
3. LiteLLM/OpenRouter pass-through / byte-exact caching — safety net below ~1024-token floor
9. OpenShell seam (NVIDIA, isolation)
ToolExecutor abstraction in Phase 1 → local by default. Phase 7 Admin/write supervisor runs inside openshell sandbox create with YAML policy (deny everything except OpenProject API). Isolation only where writes/external systems exist.
10. Implementation order
Phase 0 — Bootstrap (½ day): fix compose → docker compose up -d → verify remote OpenProject curl → requirements.txt → litellm_config.yaml → .env.example → verify 17 MCP tools load via adapters (throwaway script).
Phase 1 — SOLID skeleton (1 day): agent/config.py, llm.py, state.py, guardrails.py, hierarchy.py, factories.py.
Phase 2 — Walking skeleton (1–2 days): graph.py (START → orchestrator → supervisor → error_check → synthesize → FINISH) + nodes/ + api/main.py (POST /v1/chat, GET /health); Langfuse wired; target: "how many open work packages in project X?" E2E.
Phase 3 — Insights (1–2 days): insights/store.py + GET /v1/insights?since= → frontend reading without human prompt.
Phase 4 — Ambient (1–2 days): runner.py APScheduler + schedules.yaml (morning standup + hourly health) + /webhook/openproject with Redis debounce.
Phase 5 — HITL (½–1 day): 4 write tools behind HumanInTheLoopMiddleware; GET /approvals, POST /approve|/reject via Command(resume=...).
Phase 6 — Hardening (1 day): error retry (reduced toolset) → graceful partial answer, never raw tracebacks; needs_clarification edge; schedule failure tracking in /health.
Phase 7+ (deferred): Admin supervisor in OpenShell; Agentic RAG on Qdrant; Mem0; streaming; LLMLite-style gateway upgrade beyond LiteLLM.
11. Definition of Done (Phase 1–6)
✅ /v1/chat answers via both supervisors • ✅ 2 scheduled jobs write insight rows frontend reads • ✅ webhook trigger debounced • ✅ write tools blocked behind approval • ✅ every run traced in Langfuse • ✅ no raw tracebacks • ✅ all persisted per §7.
12. .env keys
OPENROUTER_API_KEY, OLLAMA_BASE_URL/OLLAMA_MODEL, OPENPROJECT_APIROOT, OPENPROJECT_TOKEN, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, DATABASE_URL, REDIS_URL, plus optional LITELLM_MASTER_KEY.