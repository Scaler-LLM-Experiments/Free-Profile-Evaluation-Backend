"""
Test script to verify Quick Wins logic is working correctly.
"""

import json
from quick_wins_logic import generate_quick_wins


def test_scenario(name, background, quiz_responses):
    """Test a specific scenario and print results."""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {name}")
    print(f"{'='*80}")
    print(f"Background: {background}")
    print(f"Quiz Responses:")
    for key, value in quiz_responses.items():
        print(f"  {key}: {value}")

    quick_wins = generate_quick_wins(background, quiz_responses)

    print(f"\nGenerated Quick Wins ({len(quick_wins)} items):")
    for i, win in enumerate(quick_wins, 1):
        print(f"\n{i}. {win['title']} [{win['icon']}]")
        print(f"   {win['description']}")


# Test Scenario 1: Tech user with strong system design knowledge
print("\n" + "="*80)
print("TESTING QUICK WINS LOGIC")
print("="*80)

test_scenario(
    "Tech SWE-Product, 3-5 years, Strong System Design",
    background="tech",
    quiz_responses={
        "currentRole": "swe-product",
        "experience": "3-5",
        "targetRole": "faang-sde",
        "problemSolving": "51-100",
        "systemDesign": "multiple",  # User knows system design VERY WELL
        "portfolio": "active-5+",
        "mockInterviews": "monthly"
    }
)

test_scenario(
    "Tech SWE-Product, 3-5 years, No System Design",
    background="tech",
    quiz_responses={
        "currentRole": "swe-product",
        "experience": "3-5",
        "targetRole": "faang-sde",
        "problemSolving": "51-100",
        "systemDesign": "not-yet",  # User doesn't know system design
        "portfolio": "active-5+",
        "mockInterviews": "monthly"
    }
)

test_scenario(
    "Tech SWE-Product, 3-5 years, Some System Design",
    background="tech",
    quiz_responses={
        "currentRole": "swe-product",
        "experience": "3-5",
        "targetRole": "faang-sde",
        "problemSolving": "51-100",
        "systemDesign": "once",  # User has some system design knowledge
        "portfolio": "limited-1-5",
        "mockInterviews": "monthly"
    }
)

test_scenario(
    "Non-Tech to Backend, 0-2 years",
    background="non-tech",
    quiz_responses={
        "currentRole": "non-tech",
        "experience": "0-2",
        "targetRole": "backend",
        "problemSolving": "11-50",
        "systemDesign": "not-yet",
        "portfolio": "none",
        "mockInterviews": "never"
    }
)

test_scenario(
    "Student with No Portfolio",
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

# Analyze logic flow
print("\n" + "="*80)
print("LOGIC ANALYSIS")
print("="*80)

print("""
ISSUES TO FIX:

1. Quick Wins Prioritization:
   - Currently appending all matching quick wins, then taking top 5
   - This can lead to low-priority wins showing up before high-priority ones
   - NEED: Prioritize based on impact and relevance

2. Duplicate/Conflicting Recommendations:
   - User with systemDesign='multiple' should get ADVANCED recommendations
   - User with systemDesign='not-yet' should get BEGINNER recommendations
   - Currently both might show up in the same list

3. Missing Context Awareness:
   - Should consider combinations (e.g., high experience + low problem solving)
   - Should avoid generic recommendations for advanced users

4. Portfolio + System Design Priority:
   - If user has active portfolio, don't suggest "create GitHub account"
   - If user has multiple system design, don't suggest beginner videos

RECOMMENDATIONS:

1. Use weighted priority system
2. Add exclusion rules (if X, then don't show Y)
3. Ensure most impactful wins appear first
4. Consider user's overall level (beginner/intermediate/advanced)
""")
