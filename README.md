# Learning Path Recommender — Backend (Core AI/ML Engine)

HCLTech AMPLified AI Challenge — build track.

## What's implemented (Stages 1–4, all runnable with zero API keys)

- **Stage 1 — Profiling**: `app/services/profiler.py` — keyword-matching baseline that maps free text to target skills. Swap in LLM structured extraction before submission (see TODO comment in the file).
- **Stage 2 — Core engine**: `app/graph/skill_graph.py` (NetworkX DAG) + `app/services/gap_detection.py` + `app/services/path_generator.py`. This is the spine — topological sort over the prerequisite DAG, constrained to only the skills the learner actually needs.
- **Stage 3 — Explainability**: `app/services/explainer.py` — every explanation is grounded in real prerequisite edges and gap scores, not invented. Template-based baseline; swap in an LLM rewrite pass for fluency without touching the grounding logic.
- **Stage 4 — Adaptation**: `app/services/adaptation.py` — post-assessment score updates the learner's skill level and regenerates the remaining path. This is the "DAG visibly reshapes" demo moment.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI — useful for the frontend teammate to explore the contract without reading code.

## API contract (for the frontend teammate)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/profile/{learner_id}` | POST | Submit intake form/chat → returns structured `LearnerProfile`, also generates initial path |
| `/api/path/{learner_id}` | GET | Fetch the current `LearningPath` (ordered steps for the DAG viz) |
| `/api/path/{learner_id}/explain` | POST | Get grounded explanation for one step (body: `{learner_id, skill_id}`) |
| `/api/path/{learner_id}/assess` | POST | Submit assessment score → returns updated path + human-readable changes (body: `{learner_id, skill_id, score}`) |

All request/response shapes are defined in `app/models/schemas.py` — that file is the contract. Don't change field names there without telling the frontend/data teammates.

## What to extend before submission

1. **Seed data**: `app/data/seed_skills.py` has ~20 nodes for Backend Development. Extend to 40–60 nodes (per team plan) — add depth in databases/system-design/deployment rather than new domains.
2. **Profiler**: swap keyword matching for LLM structured extraction (`.with_structured_output()` in LangChain, or raw function-calling).
3. **Explainer**: pass `grounded_on` facts into an LLM for a more natural rewrite — grounding logic doesn't change.
4. **Persistence**: `app/api/routes.py` uses an in-memory dict (`_STORE`) — swap for Postgres when ready. Service functions are DB-agnostic already, so this only touches `routes.py`.
5. **Real resource data**: `Resource` objects in `seed_skills.py` are placeholders — wire in YouTube/Coursera API results (data teammate's task).

## Project structure

```
app/
├── models/schemas.py       # Pydantic contracts — read this first
├── data/seed_skills.py     # Skill taxonomy (extend this)
├── graph/skill_graph.py    # NetworkX DAG wrapper
├── services/
│   ├── profiler.py         # Stage 1
│   ├── gap_detection.py    # Stage 2a
│   ├── path_generator.py   # Stage 2b (the spine)
│   ├── explainer.py        # Stage 3
│   └── adaptation.py       # Stage 4
├── api/routes.py           # FastAPI endpoints
└── main.py                 # App entrypoint
```
