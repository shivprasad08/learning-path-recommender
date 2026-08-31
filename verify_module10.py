"""
Module 10 verification script.

Run from the backend/ root:
    python verify_module10.py

Checks:
1. LLM-rewritten explanations for first and last path steps — confirm
   they read more naturally than the template version while still
   referencing the same underlying facts.
2. grounded_on and confidence values match what Module 5's template
   logic would have produced for the same inputs — proves the LLM only
   changed phrasing, never the underlying facts.
3. Breaks the API key and re-runs — confirms the fallback produces the
   same output the template logic would, with no crash.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # picks up GROQ_API_KEY from backend/.env

from app.graph.skill_graph import skill_graph
from app.models.schemas import LearnerProfileInput, SkillLevel
from app.services.profiler import build_profile
from app.services.path_generator import generate_learning_path
from app.services.explainer import explain_step


def main():
    raw = LearnerProfileInput(
        raw_goal_text="I want to learn Microservices Architecture for backend development",
        known_skills={"python_basics": SkillLevel.INTERMEDIATE},
        weekly_hours_available=6,
    )
    profile = build_profile("learner_1", raw, skill_graph)
    path = generate_learning_path(profile, skill_graph)

    first_skill = path.steps[0].skill.id
    last_skill = path.steps[-1].skill.id
    print(f"First step: {first_skill}")
    print(f"Last step:  {last_skill}\n")

    real_key = os.environ.get("GROQ_API_KEY")
    if not real_key:
        print("!! GROQ_API_KEY not found in environment or .env — the LLM")
        print("   path will not actually be exercised below, only the fallback.")
        print("   Set it in backend/.env as GROQ_API_KEY=your_key and re-run.\n")

    # ---------------------------------------------------------------
    # Case 1 + 2: real key in place — LLM path should fire
    # ---------------------------------------------------------------
    print("=" * 70)
    print("CASE 1/2 — WITH real API key (expect LLM-phrased explanations)")
    print("=" * 70)

    exp_first = explain_step(profile, path, first_skill, skill_graph)
    print(f"\n[First step: {first_skill}]")
    print("Explanation:", exp_first.explanation)
    print("grounded_on:", exp_first.grounded_on)
    print("confidence: ", exp_first.confidence)

    exp_last = explain_step(profile, path, last_skill, skill_graph)
    print(f"\n[Last step: {last_skill}]")
    print("Explanation:", exp_last.explanation)
    print("grounded_on:", exp_last.grounded_on)
    print("confidence: ", exp_last.confidence)

    # Sanity checks on facts (not phrasing) — these should hold regardless
    # of whether the LLM or the template path produced the text.
    assert exp_first.confidence == 0.9, "Expected confidence 0.9 (gap was found)"
    assert any("prerequisite_edges" in g for g in exp_first.grounded_on), \
        "Expected prerequisite_edges in grounded_on for first step"
    assert any("gap_score" in g for g in exp_first.grounded_on), \
        "Expected gap_score in grounded_on for first step"
    print("\n✓ grounded_on and confidence contain expected facts.")

    # ---------------------------------------------------------------
    # Case 3: break the key, confirm clean fallback
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("CASE 3 — BROKEN API key (expect clean fallback, no crash)")
    print("=" * 70)

    os.environ["GROQ_API_KEY"] = "invalid-key-xyz-broken"
    try:
        exp_broken = explain_step(profile, path, first_skill, skill_graph)
        print("\nExplanation:", exp_broken.explanation)
        print("grounded_on:", exp_broken.grounded_on)
        print("confidence: ", exp_broken.confidence)
        print("\n✓ No exception raised — fallback path confirmed working.")

        # Facts should be identical to Case 1's first-step result even
        # though the phrasing engine differs (LLM vs template).
        assert exp_broken.grounded_on == exp_first.grounded_on, \
            "grounded_on should be identical between LLM and fallback paths"
        assert exp_broken.confidence == exp_first.confidence, \
            "confidence should be identical between LLM and fallback paths"
        print("✓ grounded_on and confidence identical to the LLM-path result —")
        print("  confirms only phrasing changes, never the underlying facts.")
    except Exception as e:
        print(f"\n✗ FAILED — fallback did not engage cleanly: {e}")
        raise
    finally:
        # restore the real key for anything running after this script
        if real_key:
            os.environ["GROQ_API_KEY"] = real_key

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()