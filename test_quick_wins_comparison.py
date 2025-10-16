"""
Compare v1 vs v2 Quick Wins logic.
"""

from quick_wins_logic import generate_quick_wins as generate_v1
from quick_wins_logic_v2 import generate_quick_wins as generate_v2


def compare_scenario(name, background, quiz_responses):
    """Compare v1 vs v2 for a scenario."""
    print(f"\n{'='*100}")
    print(f"SCENARIO: {name}")
    print(f"{'='*100}")
    print(f"Profile: {quiz_responses.get('currentRole')}, {quiz_responses.get('experience')} years, " +
          f"targeting {quiz_responses.get('targetRole')}")
    print(f"Skills: {quiz_responses.get('problemSolving')} problems solved, " +
          f"System Design: {quiz_responses.get('systemDesign')}, " +
          f"Portfolio: {quiz_responses.get('portfolio')}")

    v1_wins = generate_v1(background, quiz_responses)
    v2_wins = generate_v2(background, quiz_responses)

    print(f"\n{'V1 (Current)':<50} | V2 (Improved)")
    print("-" * 100)

    for i in range(max(len(v1_wins), len(v2_wins))):
        v1_title = v1_wins[i]["title"] if i < len(v1_wins) else ""
        v2_title = v2_wins[i]["title"] if i < len(v2_wins) else ""

        print(f"{i+1}. {v1_title:<46} | {v2_title}")


print("\n" + "="*100)
print("QUICK WINS LOGIC COMPARISON: V1 vs V2")
print("="*100)

# Scenario 1: Advanced user should NOT get beginner recommendations
compare_scenario(
    "Advanced Tech User (Should get ADVANCED recommendations)",
    background="tech",
    quiz_responses={
        "currentRole": "swe-product",
        "experience": "5-8",
        "targetRole": "faang-sde",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+",
        "mockInterviews": "weekly"
    }
)

# Scenario 2: Beginner should NOT get production-ready API recommendation
compare_scenario(
    "Absolute Beginner (Should get BEGINNER recommendations)",
    background="tech",
    quiz_responses={
        "currentRole": "student-freshgrad",
        "experience": "0",
        "targetRole": "backend-sde",
        "problemSolving": "0-10",
        "systemDesign": "not-yet",
        "portfolio": "none",
        "mockInterviews": "never"
    }
)

# Scenario 3: Non-tech beginner
compare_scenario(
    "Non-Tech Career Switcher",
    background="non-tech",
    quiz_responses={
        "currentRole": "non-tech",
        "experience": "5+",
        "targetRole": "backend",
        "problemSolving": "11-50",
        "systemDesign": "not-yet",
        "portfolio": "none",
        "mockInterviews": "never"
    }
)

# Scenario 4: Intermediate tech user
compare_scenario(
    "Intermediate Tech User",
    background="tech",
    quiz_responses={
        "currentRole": "swe-service",
        "experience": "3-5",
        "targetRole": "faang-sde",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "limited-1-5",
        "mockInterviews": "monthly"
    }
)

print("\n" + "="*100)
print("KEY IMPROVEMENTS IN V2:")
print("="*100)
print("""
1. SMART PRIORITIZATION
   - Quick wins sorted by impact/priority (not just code order)
   - Most critical recommendations appear first

2. USER LEVEL DETECTION
   - Automatically determines if user is beginner/intermediate/advanced
   - Tailors recommendations to their actual skill level

3. REALISTIC RECOMMENDATIONS
   - Beginners don't get "production-ready API" tasks
   - Advanced users don't get "watch beginner videos"

4. CONTEXT-AWARE EXCLUSIONS
   - Skips irrelevant recommendations (e.g., "create GitHub" for users with active portfolio)
   - Considers skill combinations (experience + problem solving + system design)

5. FOCUSED & ACTIONABLE
   - Fewer but more impactful recommendations
   - Clear progression path based on current level

RECOMMENDATION: Replace quick_wins_logic.py with quick_wins_logic_v2.py
""")
