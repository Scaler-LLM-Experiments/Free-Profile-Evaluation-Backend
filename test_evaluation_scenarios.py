"""
Comprehensive test suite for the Profile Evaluation system.

Tests 20+ realistic user scenarios covering:
- Different backgrounds (tech/non-tech)
- Different experience levels
- Different skill combinations
- Edge cases (contradictions, gaps)
- Different target roles and companies

Run with: python test_evaluation_scenarios.py
"""

from typing import Any, Dict
from scoring_logic import calculate_profile_strength
from quick_wins_logic import generate_quick_wins
from job_descriptions import generate_job_opportunities
from tools_logic import generate_tool_recommendations


# ============================================================================
# TEST SCENARIOS
# ============================================================================

TECH_SCENARIOS = [
    # === JUNIOR/ENTRY LEVEL (0-2 years) ===
    {
        "name": "Fresh Grad - Active Learner",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-service",
            "experience": "0-2",
            "targetRole": "backend-sde",
            "problemSolving": "51-100",
            "systemDesign": "not-yet",
            "portfolio": "limited-1-5",
            "currentSkill": "backend",
            "targetCompany": "product"
        },
        "expected": {
            "score_range": (30, 50),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Leetcode Grinder - No Projects",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-service",
            "experience": "0-2",
            "targetRole": "faang-sde",
            "problemSolving": "100+",
            "systemDesign": "not-yet",
            "portfolio": "none",
            "currentSkill": "backend",
            "targetCompany": "faang"
        },
        "expected": {
            "score_range": (25, 40),  # Capped - no real experience
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Fresh Grad - Complete Beginner",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-service",
            "experience": "0-2",
            "targetRole": "backend-sde",
            "problemSolving": "0-10",
            "systemDesign": "not-yet",
            "portfolio": "none",
            "currentSkill": "backend",
            "targetCompany": "service"
        },
        "expected": {
            "score_range": (15, 30),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },

    # === MID LEVEL (3-5 years) ===
    {
        "name": "Mid-Level - Balanced Profile",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "3-5",
            "targetRole": "backend-sde",
            "problemSolving": "51-100",
            "systemDesign": "once",
            "portfolio": "limited-1-5",
            "currentSkill": "backend",
            "targetCompany": "unicorns"
        },
        "expected": {
            "score_range": (45, 65),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Mid-Level - Contradictory (SD expert without coding)",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-service",
            "experience": "3-5",
            "targetRole": "tech-lead",
            "problemSolving": "0-10",  # Claims SD expertise but no coding practice!
            "systemDesign": "multiple",
            "portfolio": "none",
            "currentSkill": "backend",
            "targetCompany": "faang"
        },
        "expected": {
            "score_range": (15, 35),  # Should get penalty
            "has_contradictions": True,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Mid-Level - Fullstack with Active Projects",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "3-5",
            "targetRole": "fullstack-sde",
            "problemSolving": "100+",
            "systemDesign": "once",
            "portfolio": "active-5+",
            "currentSkill": "fullstack",
            "targetCompany": "startups"
        },
        "expected": {
            "score_range": (55, 75),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },

    # === SENIOR LEVEL (5-8 years) ===
    {
        "name": "Senior - Strong System Design",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "5-8",
            "targetRole": "senior-faang",
            "problemSolving": "100+",
            "systemDesign": "multiple",
            "portfolio": "active-5+",
            "currentSkill": "backend",
            "targetCompany": "faang"
        },
        "expected": {
            "score_range": (85, 100),  # Should score VERY HIGH
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Senior - Rusty Skills",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "5-8",
            "targetRole": "tech-lead",
            "problemSolving": "0-10",  # Senior but not practicing!
            "systemDesign": "once",
            "portfolio": "inactive",
            "currentSkill": "backend",
            "targetCompany": "product"
        },
        "expected": {
            "score_range": (35, 55),  # Should flag contradiction
            "has_contradictions": True,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Senior - DevOps Engineer",
        "background": "tech",
        "quiz": {
            "currentRole": "devops",
            "experience": "5-8",
            "targetRole": "devops-sre",
            "problemSolving": "11-50",
            "systemDesign": "multiple",
            "portfolio": "limited-1-5",
            "currentSkill": "cloud",
            "targetCompany": "unicorns"
        },
        "expected": {
            "score_range": (65, 85),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },

    # === STAFF/PRINCIPAL (8+ years) ===
    {
        "name": "Staff Engineer - Excellent Profile",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "8+",
            "targetRole": "tech-lead",
            "problemSolving": "100+",
            "systemDesign": "multiple",
            "portfolio": "active-5+",
            "currentSkill": "backend",
            "targetCompany": "faang"
        },
        "expected": {
            "score_range": (90, 100),  # Peak score
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Staff - Architect Transitioning",
        "background": "tech",
        "quiz": {
            "currentRole": "swe-product",
            "experience": "8+",
            "targetRole": "tech-lead",
            "problemSolving": "11-50",  # Transitioned to architecture
            "systemDesign": "multiple",
            "portfolio": "inactive",
            "currentSkill": "backend",
            "targetCompany": "product"
        },
        "expected": {
            "score_range": (65, 80),  # Good but not peak
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
]

NON_TECH_SCENARIOS = [
    # === NON-TECH BACKGROUNDS ===
    {
        "name": "Non-Tech - Complete Beginner",
        "background": "non-tech",
        "quiz": {
            "currentRole": "non-tech",
            "experience": "0",
            "targetRole": "backend-dev",
            "codeComfort": "complete-beginner",
            "stepsTaken": "just-exploring",
            "timePerWeek": "0-2"
        },
        "expected": {
            "score_range": (15, 30),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Non-Tech - Serious Career Switcher",
        "background": "non-tech",
        "quiz": {
            "currentRole": "non-tech",
            "experience": "5+",
            "targetRole": "fullstack-dev",
            "codeComfort": "learning",
            "stepsTaken": "completed-course",
            "timePerWeek": "10+"
        },
        "expected": {
            "score_range": (60, 80),  # Good commitment
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Non-Tech - IT Services Background",
        "background": "non-tech",
        "quiz": {
            "currentRole": "it-services",
            "experience": "3-5",
            "targetRole": "backend-dev",
            "codeComfort": "beginner",
            "stepsTaken": "self-learning",
            "timePerWeek": "6-10"
        },
        "expected": {
            "score_range": (45, 65),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Non-Tech - Technical Role (QA/Support)",
        "background": "non-tech",
        "quiz": {
            "currentRole": "technical",
            "experience": "3-5",
            "targetRole": "fullstack-dev",
            "codeComfort": "confident",
            "stepsTaken": "built-projects",
            "timePerWeek": "10+"
        },
        "expected": {
            "score_range": (70, 90),  # Strong profile
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Non-Tech - Data Analyst Aspirant",
        "background": "non-tech",
        "quiz": {
            "currentRole": "non-tech",
            "experience": "0-2",
            "targetRole": "data-analyst",
            "codeComfort": "beginner",
            "stepsTaken": "completed-course",
            "timePerWeek": "3-5"
        },
        "expected": {
            "score_range": (40, 60),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
    {
        "name": "Non-Tech - ML Aspirant with Bootcamp",
        "background": "non-tech",
        "quiz": {
            "currentRole": "non-tech",
            "experience": "0",
            "targetRole": "data-ml",
            "codeComfort": "learning",
            "stepsTaken": "bootcamp",
            "timePerWeek": "10+"
        },
        "expected": {
            "score_range": (45, 65),
            "has_contradictions": False,
            "quick_wins_count": (3, 5),
            "opportunities_count": (5, 7),
            "tools_count": (5, 8)
        }
    },
]

# ============================================================================
# TEST RUNNER
# ============================================================================

def run_test_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test scenario and return results."""
    background = scenario["background"]
    quiz = scenario["quiz"]
    expected = scenario["expected"]

    # Run all logic functions
    scoring_result = calculate_profile_strength(background, quiz)
    quick_wins = generate_quick_wins(background, quiz)
    opportunities = generate_job_opportunities(background, quiz)
    tools = generate_tool_recommendations(background, quiz)

    # Validate results
    results = {
        "name": scenario["name"],
        "passed": True,
        "failures": [],
        "results": {
            "score": scoring_result["score"],
            "has_contradictions": scoring_result["has_contradictions"],
            "quick_wins_count": len(quick_wins),
            "opportunities_count": len(opportunities),
            "tools_count": len(tools),
            "breakdown": scoring_result.get("breakdown", {})
        }
    }

    # Check score range
    score_min, score_max = expected["score_range"]
    if not (score_min <= scoring_result["score"] <= score_max):
        results["passed"] = False
        results["failures"].append(
            f"Score {scoring_result['score']} not in expected range ({score_min}-{score_max})"
        )

    # Check contradictions
    if scoring_result["has_contradictions"] != expected["has_contradictions"]:
        results["passed"] = False
        results["failures"].append(
            f"Contradictions: got {scoring_result['has_contradictions']}, expected {expected['has_contradictions']}"
        )

    # Check quick wins count
    qw_min, qw_max = expected["quick_wins_count"]
    if not (qw_min <= len(quick_wins) <= qw_max):
        results["passed"] = False
        results["failures"].append(
            f"Quick wins count {len(quick_wins)} not in expected range ({qw_min}-{qw_max})"
        )

    # Check opportunities count
    opp_min, opp_max = expected["opportunities_count"]
    if not (opp_min <= len(opportunities) <= opp_max):
        results["passed"] = False
        results["failures"].append(
            f"Opportunities count {len(opportunities)} not in expected range ({opp_min}-{opp_max})"
        )

    # Check tools count
    tools_min, tools_max = expected["tools_count"]
    if not (tools_min <= len(tools) <= tools_max):
        results["passed"] = False
        results["failures"].append(
            f"Tools count {len(tools)} not in expected range ({tools_min}-{tools_max})"
        )

    # Check for banned tools (exact matches to avoid false positives like "GitHub Actions")
    banned_tools_patterns = [
        ("leetcode", "LeetCode"),
        ("hackerrank", "HackerRank"),
        ("coursera", "Coursera"),
        ("udemy", "Udemy"),
        ("geeksforgeeks", "GeeksForGeeks"),
        ("vs code", "VS Code"),
        ("intellij idea", "IntelliJ IDEA"),
    ]
    # Special case: Check for standalone "GitHub" or "GitLab", not "GitHub Actions"
    for tool in tools:
        tool_lower = tool.lower()
        # Check patterns
        for pattern, name in banned_tools_patterns:
            if pattern in tool_lower:
                results["passed"] = False
                results["failures"].append(f"BANNED TOOL DETECTED: {tool}")
                break
        # Check for GitHub/GitLab as standalone tools (not GitHub Actions, etc.)
        if " github" in f" {tool_lower}" and "actions" not in tool_lower:
            results["passed"] = False
            results["failures"].append(f"BANNED TOOL DETECTED: {tool}")
        if " gitlab" in f" {tool_lower}" and "ci" not in tool_lower:
            results["passed"] = False
            results["failures"].append(f"BANNED TOOL DETECTED: {tool}")

    return results


def run_all_tests():
    """Run all test scenarios and print results."""
    all_scenarios = TECH_SCENARIOS + NON_TECH_SCENARIOS

    print("=" * 100)
    print("COMPREHENSIVE PROFILE EVALUATION TEST SUITE")
    print("=" * 100)
    print(f"\nRunning {len(all_scenarios)} test scenarios...\n")

    passed = 0
    failed = 0

    for scenario in all_scenarios:
        result = run_test_scenario(scenario)

        if result["passed"]:
            print(f"✅ PASS: {result['name']}")
            print(f"   Score: {result['results']['score']}/100")
            print(f"   Contradictions: {result['results']['has_contradictions']}")
            print(f"   Quick Wins: {result['results']['quick_wins_count']}")
            print(f"   Opportunities: {result['results']['opportunities_count']}")
            print(f"   Tools: {result['results']['tools_count']}")
            passed += 1
        else:
            print(f"❌ FAIL: {result['name']}")
            print(f"   Score: {result['results']['score']}/100")
            print(f"   Failures:")
            for failure in result["failures"]:
                print(f"     - {failure}")
            failed += 1

        print()

    print("=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)
    print(f"Total: {len(all_scenarios)}")
    print(f"Passed: {passed} ({passed/len(all_scenarios)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(all_scenarios)*100:.1f}%)")
    print()

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} TEST(S) FAILED - Review output above")

    print("=" * 100)


def print_detailed_example():
    """Print a detailed example of one scenario."""
    print("\n" + "=" * 100)
    print("DETAILED EXAMPLE: Senior Engineer with Strong System Design")
    print("=" * 100)

    scenario = {
        "currentRole": "swe-product",
        "experience": "5-8",
        "targetRole": "senior-faang",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+",
        "currentSkill": "backend",
        "targetCompany": "faang"
    }

    scoring = calculate_profile_strength("tech", scenario)
    quick_wins = generate_quick_wins("tech", scenario)
    opportunities = generate_job_opportunities("tech", scenario)
    tools = generate_tool_recommendations("tech", scenario)

    print(f"\nProfile Strength Score: {scoring['score']}/100")
    print(f"Has Contradictions: {scoring['has_contradictions']}")
    print(f"\nScore Breakdown:")
    for key, value in scoring.get('breakdown', {}).items():
        print(f"  - {key}: {value}")

    print(f"\nQuick Wins ({len(quick_wins)}):")
    for i, qw in enumerate(quick_wins, 1):
        print(f"  {i}. [{qw['icon']}] {qw['title']}")
        print(f"     {qw['description']}")

    print(f"\nJob Opportunities ({len(opportunities)}):")
    for i, opp in enumerate(opportunities, 1):
        print(f"  {i}. {opp}")

    print(f"\nRecommended Tools ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool}")

    print("=" * 100)


if __name__ == "__main__":
    run_all_tests()
    print_detailed_example()
