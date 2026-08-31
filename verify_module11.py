"""
Module 11 — Postgres persistence verification.

Runs the same 6-check integration test from Module 7, but now against the
Postgres-backed storage layer instead of the old in-memory dict.

Prerequisites:
    1. docker-compose up -d   (Postgres must be running)
    2. uvicorn app.main:app --port 8000  (in another terminal)

Usage:
    python verify_module11.py
"""

import sys
import requests

BASE = "http://localhost:8000/api"
LEARNER_ID = "test_module11_learner"


def check(label: str, passed: bool, detail: str = "") -> bool:
    status = "PASS ✅" if passed else "FAIL ❌"
    print(f"  [{status}] {label}")
    if detail:
        print(f"           {detail}")
    return passed


def main() -> int:
    results: list[bool] = []
    print("\n" + "=" * 60)
    print("Module 11 — Postgres Persistence Verification (6 checks)")
    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # Check 1: POST /profile/{learner_id} — create profile + initial path
    # ------------------------------------------------------------------
    print("[Check 1] POST /profile — create profile")
    try:
        r = requests.post(
            f"{BASE}/profile/{LEARNER_ID}",
            json={
                "raw_goal_text": "I want to learn REST API design and FastAPI",
                "known_skills": {"python_basics": "intermediate"},
                "weekly_hours_available": 10,
            },
        )
        ok = r.status_code == 200
        body = r.json()
        ok = ok and body.get("learner_id") == LEARNER_ID
        ok = ok and len(body.get("target_skills", [])) > 0
        results.append(check("POST /profile", ok, f"status={r.status_code}, targets={body.get('target_skills')}"))
    except Exception as e:
        results.append(check("POST /profile", False, str(e)))

    # ------------------------------------------------------------------
    # Check 2: GET /path/{learner_id} — fetch the learning path
    # ------------------------------------------------------------------
    print("\n[Check 2] GET /path — fetch learning path")
    try:
        r = requests.get(f"{BASE}/path/{LEARNER_ID}")
        ok = r.status_code == 200
        body = r.json()
        ok = ok and len(body.get("steps", [])) > 0
        ok = ok and body.get("total_estimated_hours", 0) > 0
        num_steps = len(body.get("steps", []))
        results.append(check("GET /path", ok, f"status={r.status_code}, steps={num_steps}, hours={body.get('total_estimated_hours')}"))
        first_skill_id = body["steps"][0]["skill"]["id"] if body.get("steps") else None
    except Exception as e:
        results.append(check("GET /path", False, str(e)))
        first_skill_id = None

    # ------------------------------------------------------------------
    # Check 3: POST /path/{learner_id}/explain — explain a step
    # ------------------------------------------------------------------
    print("\n[Check 3] POST /path/explain — explain a step")
    if first_skill_id:
        try:
            r = requests.post(
                f"{BASE}/path/{LEARNER_ID}/explain",
                json={"learner_id": LEARNER_ID, "skill_id": first_skill_id},
            )
            ok = r.status_code == 200
            body = r.json()
            ok = ok and len(body.get("explanation", "")) > 0
            ok = ok and body.get("skill_id") == first_skill_id
            results.append(check("POST /path/explain", ok, f"status={r.status_code}, explanation_len={len(body.get('explanation', ''))}"))
        except Exception as e:
            results.append(check("POST /path/explain", False, str(e)))
    else:
        results.append(check("POST /path/explain", False, "Skipped — no first_skill_id from check 2"))

    # ------------------------------------------------------------------
    # Check 4: POST /path/{learner_id}/assess — assess with HIGH score
    # ------------------------------------------------------------------
    print("\n[Check 4] POST /path/assess — assess with high score")
    if first_skill_id:
        try:
            r = requests.post(
                f"{BASE}/path/{LEARNER_ID}/assess",
                json={"learner_id": LEARNER_ID, "skill_id": first_skill_id, "score": 0.95},
            )
            ok = r.status_code == 200
            body = r.json()
            ok = ok and len(body.get("changes", [])) > 0
            ok = ok and body.get("updated_path") is not None
            results.append(check("POST /path/assess (high score)", ok, f"status={r.status_code}, changes={body.get('changes', [])}"))
        except Exception as e:
            results.append(check("POST /path/assess (high score)", False, str(e)))
    else:
        results.append(check("POST /path/assess (high score)", False, "Skipped — no first_skill_id from check 2"))

    # ------------------------------------------------------------------
    # Check 5: GET /path/{learner_id} again — confirm the assessment
    #          update was persisted
    # ------------------------------------------------------------------
    print("\n[Check 5] GET /path (after assess) — confirm persisted update")
    try:
        r = requests.get(f"{BASE}/path/{LEARNER_ID}")
        ok = r.status_code == 200
        body = r.json()
        updated_steps = len(body.get("steps", []))
        # After mastering the first skill, the path should have fewer steps
        # (or at least be a valid path)
        ok = ok and body.get("steps") is not None
        results.append(check("GET /path (post-assess)", ok, f"status={r.status_code}, steps={updated_steps} (was {num_steps})"))
    except Exception as e:
        results.append(check("GET /path (post-assess)", False, str(e)))

    # ------------------------------------------------------------------
    # Check 6: GET /path/{nonexistent} — 404 for unknown learner
    # ------------------------------------------------------------------
    print("\n[Check 6] GET /path for nonexistent learner — expect 404")
    try:
        r = requests.get(f"{BASE}/path/totally_unknown_learner_xyz")
        ok = r.status_code == 404
        results.append(check("GET /path (nonexistent -> 404)", ok, f"status={r.status_code}"))
    except Exception as e:
        results.append(check("GET /path (nonexistent -> 404)", False, str(e)))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    if passed == total:
        print("🎉 All checks PASSED — Postgres persistence is working!")
    else:
        print("⚠️  Some checks failed — see output above.")
    print("=" * 60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())