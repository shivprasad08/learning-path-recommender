import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.profiler import build_profile
from app.models.schemas import LearnerProfileInput
from app.graph.skill_graph import skill_graph

def run_tests():
    print("--- Case 1: Semantic understanding (NO exact keyword matches) ---")
    raw1 = LearnerProfileInput(
        raw_goal_text="I want to build scalable systems that handle millions of users",
        known_skills={},
        weekly_hours_available=10
    )
    profile1 = build_profile("u1", raw1, skill_graph)
    print(f"Goal: '{raw1.raw_goal_text}'")
    print(f"Extracted targets: {profile1.target_skills}\n")

    print("--- Case 2: Module 3 Original Verification Tests ---")
    raw2 = LearnerProfileInput(
        raw_goal_text="I need to learn python fundamentals and docker",
        known_skills={},
        weekly_hours_available=5
    )
    profile2 = build_profile("u2", raw2, skill_graph)
    print(f"Goal: '{raw2.raw_goal_text}'")
    print(f"Extracted targets: {profile2.target_skills}\n")
    
    raw3 = LearnerProfileInput(
        raw_goal_text="Just getting started with nothing in mind",
        known_skills={},
        weekly_hours_available=5
    )
    profile3 = build_profile("u3", raw3, skill_graph)
    print(f"Goal: '{raw3.raw_goal_text}'")
    print(f"Extracted targets (fallback): {profile3.target_skills}\n")

    print("--- Case 3: Broken API Key Fallback ---")
    os.environ["GROQ_API_KEY"] = "garbage_key_123"
    profile_fail = build_profile("u4", raw1, skill_graph)
    print(f"Goal: '{raw1.raw_goal_text}' (with broken API key)")
    print(f"Extracted targets (fallback keyword matching): {profile_fail.target_skills}\n")

if __name__ == "__main__":
    run_tests()
