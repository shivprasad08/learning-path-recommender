"""
Module 11 — Restart persistence check.

After running verify_module11.py (which creates data for
'test_module11_learner'), STOP the FastAPI process, START it again, and
then run this script. If the data is returned, Postgres persistence
survived the restart — the in-memory version would have lost everything.

Usage:
    1. Run verify_module11.py first (while the server is up)
    2. STOP the uvicorn process
    3. START uvicorn again: uvicorn app.main:app --port 8000
    4. python verify_module11_restart_check.py
"""

import sys
import requests

BASE = "http://localhost:8000/api"
LEARNER_ID = "test_module11_learner"


def main() -> int:
    print("\n" + "=" * 60)
    print("Module 11 — Restart Persistence Check")
    print("=" * 60 + "\n")

    print("  Fetching path for learner created BEFORE the server restart...")
    try:
        r = requests.get(f"{BASE}/path/{LEARNER_ID}")
    except requests.ConnectionError:
        print("  [FAIL ❌] Cannot connect to http://localhost:8000")
        print("            Make sure uvicorn is running after the restart.")
        return 1

    if r.status_code == 200:
        body = r.json()
        steps = len(body.get("steps", []))
        hours = body.get("total_estimated_hours", 0)
        print(f"  [PASS ✅] GET /path/{LEARNER_ID} returned 200")
        print(f"            steps={steps}, total_estimated_hours={hours}")
        print(f"\n  ✅ Data survived the server restart — Postgres persistence confirmed!")
        print("=" * 60 + "\n")
        return 0
    elif r.status_code == 404:
        print(f"  [FAIL ❌] GET /path/{LEARNER_ID} returned 404")
        print("            Data was LOST after restart — this means storage is still in-memory!")
        print("=" * 60 + "\n")
        return 1
    else:
        print(f"  [FAIL ❌] Unexpected status code: {r.status_code}")
        print(f"            Body: {r.text}")
        print("=" * 60 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())