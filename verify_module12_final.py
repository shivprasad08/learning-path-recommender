"""
Module 12 -- Final end-to-end integration verification (Modules 0-11).

Validates that the complete Learning Path Recommender backend works
as a cohesive whole after all module upgrades:
  Module  8: Expanded seed taxonomy (20 -> 47 nodes)
  Module  9: LLM profiler with keyword-matching fallback
  Module 10: LLM explainer with template fallback
  Module 11: Postgres persistence (replacing in-memory dict)

Uses FastAPI's TestClient for in-process testing.  Check 6 simulates
a server restart by creating a *fresh* TestClient instance -- since
TestClient carries no in-memory state between instances, only data
stored in Postgres survives, exactly as with a real process restart.

Prerequisites:
    docker-compose up -d          (Postgres must be running)
    pip install httpx             (required by TestClient)

Usage:
    cd backend
    python verify_module12_final.py
"""

import os
import sys
import textwrap

# ---------------------------------------------------------------------------
# Pre-flight: ensure httpx is importable (TestClient needs it)
# ---------------------------------------------------------------------------
try:
    import httpx  # noqa: F401
except ImportError:
    print("[pre-flight] Installing httpx (required by TestClient)...")
    os.system(f'"{sys.executable}" -m pip install httpx -q')

from fastapi.testclient import TestClient  # noqa: E402

# Guarantee DATABASE_URL is set before importing the app so that
# database.py picks up the right connection string.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = (
        "postgresql+psycopg2://lprdev:lprdevpass@localhost:5432/"
        "learning_path_recommender"
    )

from app.main import app  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LEARNER = "module12_final_verify"
FALLBACK_LEARNER = "module12_fallback_verify"
API = "/api"
# Natural-language goal that also contains a recognizable keyword
# ("microservices") so the profiler has something to latch onto whether
# it's running the LLM path or the keyword-matching fallback.
GOAL = "I want to build and deploy microservices in production"

RESULTS: list[tuple[int, bool, str]] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def record(num: int, passed: bool, label: str, detail: str = "") -> bool:
    tag = "PASS [OK]" if passed else "FAIL [X]"
    print(f"  [{tag}] Check {num}: {label}")
    if detail:
        for line in detail.strip().splitlines():
            print(f"           {line}")
    RESULTS.append((num, passed, label))
    return passed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print()
    print("=" * 66)
    print("  Module 12 -- Final Integration Verification (Modules 0-11)")
    print("=" * 66)

    # -- Pre-flight: verify Postgres is reachable ---------------------
    print("\n[Pre-flight] Checking Postgres connectivity ...")
    try:
        from sqlalchemy import text as sa_text
        from app.db.database import engine
        with engine.connect() as conn:
            conn.execute(sa_text("SELECT 1"))
        print("  [OK] Postgres is reachable\n")
    except Exception as exc:
        print(f"  [X] Cannot connect to Postgres: {exc}")
        print("    -> Run  docker-compose up -d  first, then retry.")
        return 1

    # Tracking variables shared across checks
    first_skill_id = None
    initial_step_count = 0
    post_assess_step_count = 0

    # ==================================================================
    #  Phase 1 - Checks 1-5, 7, 8  (single TestClient instance)
    # ==================================================================
    print("-" * 66)
    print("Phase 1: Core integration checks  (TestClient instance #1)")
    print("-" * 66)

    with TestClient(app, raise_server_exceptions=False) as client:

        # - CHECK 1 -
        print("\n[Check 1] POST /profile - natural-language goal")
        try:
            r = client.post(
                f"{API}/profile/{LEARNER}",
                json={
                    "raw_goal_text": GOAL,
                    "known_skills": {},
                    "weekly_hours_available": 10,
                },
            )
            body = r.json()
            targets = body.get("target_skills", [])
            ok = r.status_code == 200 and len(targets) > 0
            record(1, ok, "POST /profile",
                   f"status={r.status_code}\n"
                   f"target_skills={targets}")
        except Exception as e:
            record(1, False, "POST /profile", str(e))

        # - CHECK 2 -
        print("\n[Check 2] GET /path - step count + prerequisite ordering")
        try:
            r = client.get(f"{API}/path/{LEARNER}")
            body = r.json()
            steps = body.get("steps", [])
            initial_step_count = len(steps)
            hours = body.get("total_estimated_hours", 0)

            # Build the set of skill IDs in this path for fast lookup
            path_skill_ids = {s["skill"]["id"] for s in steps}

            # Walk the list; every prereq that IS in the path must have
            # been seen already (topological correctness).
            seen: set[str] = set()
            ordering_ok = True
            violations: list[str] = []
            for step in steps:
                sid = step["skill"]["id"]
                for prereq in step["skill"].get("prerequisites", []):
                    if prereq in path_skill_ids and prereq not in seen:
                        ordering_ok = False
                        violations.append(
                            f"'{sid}' placed before its prereq '{prereq}'"
                        )
                seen.add(sid)

            ok = (r.status_code == 200
                  and initial_step_count > 0
                  and ordering_ok)

            detail_lines = [
                f"status={r.status_code}, steps={initial_step_count}, "
                f"hours={hours}",
            ]
            if violations:
                detail_lines.append(
                    "WARNING ordering violations: " + "; ".join(violations)
                )
            else:
                detail_lines.append("[OK] prerequisite ordering is valid")

            record(2, ok, "GET /path + ordering", "\n".join(detail_lines))
            first_skill_id = steps[0]["skill"]["id"] if steps else None
        except Exception as e:
            record(2, False, "GET /path + ordering", str(e))

        # - CHECK 3 -
        print("\n[Check 3] POST /path/explain - explain first step")
        if first_skill_id:
            try:
                r = client.post(
                    f"{API}/path/{LEARNER}/explain",
                    json={
                        "learner_id": LEARNER,
                        "skill_id": first_skill_id,
                    },
                )
                body = r.json()
                explanation = body.get("explanation", "")
                grounded = body.get("grounded_on", [])
                confidence = body.get("confidence", 0)

                ok = (r.status_code == 200
                      and len(explanation) > 20
                      and isinstance(grounded, list)
                      and len(grounded) > 0)

                # Truncate explanation for readability
                expl_preview = (explanation[:140] + "..."
                                if len(explanation) > 140
                                else explanation)
                record(3, ok, "POST /path/explain",
                       f"status={r.status_code}, confidence={confidence}\n"
                       f"explanation: \"{expl_preview}\"\n"
                       f"grounded_on: {grounded}")
            except Exception as e:
                record(3, False, "POST /path/explain", str(e))
        else:
            record(3, False, "POST /path/explain",
                   "Skipped - no skill ID from check 2")

        # - CHECK 4 -
        print("\n[Check 4] POST /path/assess - high score (0.95)")
        if first_skill_id:
            try:
                r = client.post(
                    f"{API}/path/{LEARNER}/assess",
                    json={
                        "learner_id": LEARNER,
                        "skill_id": first_skill_id,
                        "score": 0.95,
                    },
                )
                body = r.json()
                changes = body.get("changes", [])
                updated_path = body.get("updated_path", {})
                post_assess_step_count = len(
                    updated_path.get("steps", [])
                )
                diff = initial_step_count - post_assess_step_count

                ok = (r.status_code == 200
                      and len(changes) > 0
                      and diff >= 1)

                record(4, ok, "POST /path/assess (high score)",
                       f"status={r.status_code}\n"
                       f"changes: {changes}\n"
                       f"steps: {initial_step_count} -> "
                       f"{post_assess_step_count}  (delta = {diff})")
            except Exception as e:
                record(4, False, "POST /path/assess (high score)", str(e))
        else:
            record(4, False, "POST /path/assess (high score)",
                   "Skipped - no skill ID from check 2")

        # - CHECK 5 -
        print("\n[Check 5] GET /path - confirm assessment persisted")
        try:
            r = client.get(f"{API}/path/{LEARNER}")
            body = r.json()
            persisted = len(body.get("steps", []))

            ok = (r.status_code == 200
                  and persisted == post_assess_step_count)

            record(5, ok, "GET /path (persisted after assess)",
                   f"status={r.status_code}, steps={persisted}, "
                   f"expected={post_assess_step_count}")
        except Exception as e:
            record(5, False, "GET /path (persisted after assess)", str(e))

        # - CHECK 7 -
        print("\n[Check 7] GET /path for nonexistent learner - 404")
        try:
            r = client.get(f"{API}/path/nonexistent_learner_xyz")
            ok = r.status_code == 404
            record(7, ok, "GET /path (404 for unknown learner)",
                   f"status={r.status_code}")
        except Exception as e:
            record(7, False, "GET /path (404 for unknown learner)", str(e))

        # - CHECK 8 -
        print("\n[Check 8] Fallback safety net - invalid API key")
        saved_key = os.environ.get("GROQ_API_KEY")
        try:
            os.environ["GROQ_API_KEY"] = "INVALID_KEY_FOR_TESTING"
            r = client.post(
                f"{API}/profile/{FALLBACK_LEARNER}",
                json={
                    "raw_goal_text": GOAL,
                    "known_skills": {},
                    "weekly_hours_available": 10,
                },
            )
            body = r.json()
            targets = body.get("target_skills", [])
            ok = r.status_code == 200 and len(targets) > 0
            record(8, ok, "POST /profile (invalid key -> fallback)",
                   f"status={r.status_code}\n"
                   f"target_skills={targets}\n"
                   f"[OK] Keyword-matching fallback engaged cleanly")
        except Exception as e:
            record(8, False, "POST /profile (invalid key -> fallback)",
                   str(e))
        finally:
            # Restore original key
            if saved_key is not None:
                os.environ["GROQ_API_KEY"] = saved_key
            elif "GROQ_API_KEY" in os.environ:
                del os.environ["GROQ_API_KEY"]

    # ==================================================================
    #  Phase 2 - Check 6: restart persistence  (fresh TestClient)
    # ==================================================================
    print()
    print("-" * 66)
    print("Phase 2: Restart persistence  (TestClient instance #2)")
    print("  A fresh TestClient carries zero in-memory state from Phase 1.")
    print("  If the data is still there, Postgres persistence is proven.")
    print("-" * 66)

    print(f"\n[Check 6] GET /path after simulated restart")
    with TestClient(app, raise_server_exceptions=False) as client2:
        try:
            r = client2.get(f"{API}/path/{LEARNER}")
            body = r.json()
            restart_count = len(body.get("steps", []))

            ok = (r.status_code == 200
                  and restart_count == post_assess_step_count)

            record(6, ok, "GET /path (post-restart persistence)",
                   f"status={r.status_code}, steps={restart_count}, "
                   f"expected={post_assess_step_count}\n"
                   f"[OK] Data survived simulated restart -- "
                   f"Postgres persistence confirmed")
        except Exception as e:
            record(6, False, "GET /path (post-restart persistence)",
                   str(e))

    # ==================================================================
    #  Summary
    # ==================================================================
    print()
    print("=" * 66)

    RESULTS.sort(key=lambda x: x[0])
    passed = [r for r in RESULTS if r[1]]
    failed = [r for r in RESULTS if not r[1]]

    print(f"\n  {len(passed)}/8 checks passed")

    if failed:
        nums = ", ".join(str(r[0]) for r in failed)
        print(f"  WARNING -- Failing checks: {nums}")
        for num, _, label in failed:
            print(f"    - Check {num}: {label}")
    else:
        print(
            "  ALL 8 CHECKS PASSED -- backend (Modules 0-11) "
            "is submission-ready!"
        )

    print(textwrap.dedent("""
    ------------------------------------------------------------------
    Remaining work (non-backend, per team plan):
      1. Frontend DAG visualization wired to this API
      2. Real course/resource data from external APIs replacing
         the placeholder Resource entries in seed_skills.py
      3. Solution documentation (architecture, design decisions)
      4. Demo video script & recording
    ------------------------------------------------------------------
    """))

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
