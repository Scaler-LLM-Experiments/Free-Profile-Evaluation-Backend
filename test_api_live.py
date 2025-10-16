"""
Live API Testing Script - Tests actual running backend on localhost:8000

Tests multiple scenarios and validates:
- No banned tools (LeetCode, GitHub, VS Code, Coursera)
- Specific job descriptions (not generic fluff)
- Proper scoring with new weighting
- Contradiction detection
- Quick wins quality
- Tools recommendations

Run with: python test_api_live.py
"""

import json
import requests
from typing import Dict, Any, List
import time


API_BASE_URL = "http://localhost:8000"
BANNED_TOOLS = ["leetcode", "hackerrank", "github", "gitlab", "coursera", "udemy", "vs code", "intellij"]
GENERIC_PHRASES = [
    "aligns with your",
    "matches your experience",
    "practice more",
    "learn system design",
    "improve coding",
]

# Test Scenarios
TEST_SCENARIOS = [
    {
        "name": "Senior Backend Engineer - Strong System Design",
        "description": "Should score 85-100 with system design heavily weighted",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "swe-product",
                "experience": "5-8",
                "targetRole": "senior-faang",
                "problemSolving": "100+",
                "systemDesign": "multiple",
                "portfolio": "active-5+",
                "currentSkill": "backend",
                "targetCompany": "faang",
                "currentCompany": "Razorpay",
                "mockInterviews": "monthly"
            },
            "goals": {
                "requirementType": ["better-company"],
                "targetCompany": "Google",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 85,
            "score_max": 100,
            "should_have_contradictions": False,
            "should_mention_senior_roles": True
        }
    },
    {
        "name": "Mid-Level - Contradictory Profile (SD expert without coding)",
        "description": "Should detect contradiction and apply -15 penalty",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "swe-service",
                "experience": "3-5",
                "targetRole": "tech-lead",
                "problemSolving": "0-10",  # CONTRADICTION!
                "systemDesign": "multiple",  # Claims expertise
                "portfolio": "none",
                "currentSkill": "backend",
                "targetCompany": "faang",
                "currentCompany": "TCS",
                "mockInterviews": "never"
            },
            "goals": {
                "requirementType": ["better-company"],
                "targetCompany": "Amazon",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 10,
            "score_max": 35,
            "should_have_contradictions": True,
            "should_mention_senior_roles": False
        }
    },
    {
        "name": "Junior Fullstack - Active Learner",
        "description": "Should score 30-50 with appropriate junior recommendations",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "swe-service",
                "experience": "0-2",
                "targetRole": "fullstack-sde",
                "problemSolving": "51-100",
                "systemDesign": "not-yet",
                "portfolio": "limited-1-5",
                "currentSkill": "fullstack",
                "targetCompany": "startups",
                "currentCompany": "Wipro",
                "mockInterviews": "rarely"
            },
            "goals": {
                "requirementType": ["upskilling"],
                "targetCompany": "Startup",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 30,
            "score_max": 55,
            "should_have_contradictions": False,
            "should_mention_senior_roles": False
        }
    },
    {
        "name": "LeetCode Grinder - No Real Experience",
        "description": "Should cap score at ~40 despite 100+ problems",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "swe-service",
                "experience": "0-2",
                "targetRole": "backend-sde",
                "problemSolving": "100+",  # Lots of practice
                "systemDesign": "not-yet",
                "portfolio": "none",  # But no projects!
                "currentSkill": "backend",
                "targetCompany": "faang",
                "currentCompany": "Infosys",
                "mockInterviews": "rarely"
            },
            "goals": {
                "requirementType": ["better-company"],
                "targetCompany": "Google",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 20,
            "score_max": 40,
            "should_have_contradictions": False,
            "should_mention_senior_roles": False
        }
    },
    {
        "name": "DevOps Engineer - Senior",
        "description": "Should get DevOps-specific tools and opportunities",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "devops",
                "experience": "5-8",
                "targetRole": "devops-sre",
                "problemSolving": "51-100",
                "systemDesign": "multiple",
                "portfolio": "limited-1-5",
                "currentSkill": "cloud",
                "targetCompany": "product",
                "currentCompany": "PhonePe",
                "mockInterviews": "monthly"
            },
            "goals": {
                "requirementType": ["higher-comp"],
                "targetCompany": "FAANG",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 60,
            "score_max": 90,
            "should_have_contradictions": False,
            "should_mention_devops_tools": True
        }
    },
    {
        "name": "Non-Tech - Complete Beginner",
        "description": "Should get beginner-friendly recommendations",
        "payload": {
            "background": "non-tech",
            "quizResponses": {
                "currentRole": "career-switcher",
                "experience": "0",
                "targetRole": "backend-dev",
                "problemSolving": "0-10",  # Mapped from codeComfort
                "systemDesign": "not-yet",  # Non-tech default
                "portfolio": "none",  # Non-tech default
                "mockInterviews": "never",  # Non-tech default
                "currentCompany": "Transitioning from non-tech background",
                "currentSkill": "0-10",
                "requirementType": "career-switch",
                "targetCompany": "Transitioning from non-tech background"
            },
            "goals": {
                "requirementType": ["career-switch"],
                "targetCompany": "",
                "topicOfInterest": ["web-development", "backend-development"]
            }
        },
        "validations": {
            "score_min": 10,
            "score_max": 35,
            "should_have_contradictions": False,
            "should_mention_senior_roles": False
        }
    },
    {
        "name": "Non-Tech - Serious Career Switcher",
        "description": "Should score well (60-80) with high commitment",
        "payload": {
            "background": "non-tech",
            "quizResponses": {
                "currentRole": "career-switcher",
                "experience": "5+",
                "targetRole": "fullstack-dev",
                "problemSolving": "11-50",  # Mapped from codeComfort='learning'
                "systemDesign": "not-yet",  # Non-tech default
                "portfolio": "none",  # Non-tech default
                "mockInterviews": "never",  # Non-tech default
                "currentCompany": "Transitioning from non-tech background",
                "currentSkill": "11-50",
                "requirementType": "career-switch",
                "targetCompany": "Transitioning from non-tech background"
            },
            "goals": {
                "requirementType": ["career-switch"],
                "targetCompany": "",
                "topicOfInterest": ["web-development", "fullstack-development"]
            }
        },
        "validations": {
            "score_min": 60,
            "score_max": 95,
            "should_have_contradictions": False,
            "should_mention_senior_roles": False
        }
    },
    {
        "name": "Staff Engineer - Architect Track",
        "description": "Should score 90-100 with leadership roles",
        "payload": {
            "background": "tech",
            "quizResponses": {
                "currentRole": "swe-product",
                "experience": "8+",
                "targetRole": "tech-lead",
                "problemSolving": "100+",
                "systemDesign": "multiple",
                "portfolio": "active-5+",
                "currentSkill": "backend",
                "targetCompany": "faang",
                "currentCompany": "Microsoft",
                "mockInterviews": "weekly+"
            },
            "goals": {
                "requirementType": ["level-up"],
                "targetCompany": "Google",
                "topicOfInterest": []
            }
        },
        "validations": {
            "score_min": 90,
            "score_max": 100,
            "should_have_contradictions": False,
            "should_mention_senior_roles": True,
            "should_mention_staff_roles": True
        }
    }
]


def call_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call the /evaluate endpoint and return response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/evaluate",
            json=payload,
            timeout=120  # 2 minutes timeout for OpenAI call
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API call failed: {str(e)}")
        return None


def validate_no_banned_tools(tools: List[str]) -> List[str]:
    """Check if any banned tools are present."""
    violations = []
    for tool in tools:
        tool_lower = tool.lower()
        for banned in BANNED_TOOLS:
            # Special case: GitHub Actions is OK, standalone GitHub is not
            if banned == "github" and "actions" in tool_lower:
                continue
            if banned == "gitlab" and "ci" in tool_lower:
                continue
            if banned in tool_lower:
                violations.append(f"BANNED TOOL: {tool}")
    return violations


def validate_no_generic_phrases(opportunities: List[str]) -> List[str]:
    """Check if any generic phrases are present in opportunities."""
    violations = []
    for opp in opportunities:
        opp_lower = opp.lower()
        for generic in GENERIC_PHRASES:
            if generic in opp_lower:
                violations.append(f"GENERIC PHRASE: '{generic}' in '{opp}'")
    return violations


def validate_job_descriptions(opportunities: List[str]) -> Dict[str, Any]:
    """Validate job description quality."""
    issues = []

    for opp in opportunities:
        # Check if it has a company name
        if not any(company in opp for company in ["India", "Google", "Amazon", "Microsoft", "Flipkart", "Swiggy", "Zomato", "CRED", "PhonePe", "Razorpay"]):
            issues.append(f"No specific company in: {opp}")

        # Check word count (should be concise)
        word_count = len(opp.split())
        if word_count > 25:
            issues.append(f"Too wordy ({word_count} words): {opp}")

    return {
        "total": len(opportunities),
        "issues": issues,
        "pass": len(issues) == 0
    }


def validate_quick_wins(quick_wins: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate quick wins quality."""
    issues = []

    if len(quick_wins) < 3:
        issues.append(f"Too few quick wins: {len(quick_wins)} (expected 3-5)")

    for qw in quick_wins:
        if not qw.get("title"):
            issues.append("Quick win missing title")
        if not qw.get("description"):
            issues.append("Quick win missing description")

        # Check for generic phrases
        desc = qw.get("description", "").lower()
        if "practice more" in desc or "improve coding" in desc or "learn system design" in desc:
            issues.append(f"Generic quick win: {qw.get('title')}")

    return {
        "total": len(quick_wins),
        "issues": issues,
        "pass": len(issues) == 0
    }


def run_test_scenario(scenario: Dict[str, Any], index: int, total: int) -> Dict[str, Any]:
    """Run a single test scenario and validate results."""
    print(f"\n{'='*100}")
    print(f"TEST {index}/{total}: {scenario['name']}")
    print(f"{'='*100}")
    print(f"Description: {scenario['description']}")
    print(f"\nCalling API...")

    start_time = time.time()
    response = call_api(scenario["payload"])
    elapsed = time.time() - start_time

    if not response:
        return {
            "name": scenario["name"],
            "passed": False,
            "failures": ["API call failed"],
            "elapsed": elapsed
        }

    print(f"   ✓ Response received in {elapsed:.1f}s")

    # Extract data
    profile_eval = response.get("profile_evaluation", {})
    score = profile_eval.get("profile_strength_score", 0)
    notes = profile_eval.get("profile_strength_notes", "")
    tools = profile_eval.get("recommended_tools", [])
    opportunities = profile_eval.get("opportunities_you_qualify_for", [])
    quick_wins = profile_eval.get("quick_wins", [])

    # Run validations
    validations = scenario["validations"]
    failures = []

    # 1. Score validation
    print(f"\n📊 SCORE: {score}/100")
    if not (validations["score_min"] <= score <= validations["score_max"]):
        failures.append(f"Score {score} not in expected range ({validations['score_min']}-{validations['score_max']})")
    else:
        print(f"   ✓ Score in expected range ({validations['score_min']}-{validations['score_max']})")

    # 2. Contradiction detection
    has_contradiction = "contradiction" in notes.lower() or "design expertise requires" in notes.lower()
    if has_contradiction != validations["should_have_contradictions"]:
        failures.append(f"Contradiction detection: got {has_contradiction}, expected {validations['should_have_contradictions']}")
    else:
        print(f"   ✓ Contradiction detection correct: {has_contradiction}")

    # 3. Banned tools check
    print(f"\n🔧 TOOLS: {len(tools)} recommendations")
    banned_violations = validate_no_banned_tools(tools)
    if banned_violations:
        failures.extend(banned_violations)
        print(f"   ❌ {len(banned_violations)} banned tools found!")
        for v in banned_violations:
            print(f"      - {v}")
    else:
        print(f"   ✓ No banned tools detected")

    # Print sample tools
    for i, tool in enumerate(tools[:3], 1):
        print(f"      {i}. {tool}")

    # 4. Job descriptions check
    print(f"\n💼 JOB OPPORTUNITIES: {len(opportunities)}")
    generic_violations = validate_no_generic_phrases(opportunities)
    if generic_violations:
        failures.extend(generic_violations)
        print(f"   ❌ {len(generic_violations)} generic phrases found!")
    else:
        print(f"   ✓ No generic phrases detected")

    job_validation = validate_job_descriptions(opportunities)
    if not job_validation["pass"]:
        failures.extend(job_validation["issues"])
        print(f"   ❌ {len(job_validation['issues'])} job description issues")
    else:
        print(f"   ✓ All job descriptions are specific")

    # Print sample opportunities
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"      {i}. {opp}")

    # 5. Quick wins check
    print(f"\n⚡ QUICK WINS: {len(quick_wins)}")
    qw_validation = validate_quick_wins(quick_wins)
    if not qw_validation["pass"]:
        failures.extend(qw_validation["issues"])
        print(f"   ❌ {len(qw_validation['issues'])} quick win issues")
    else:
        print(f"   ✓ Quick wins quality validated")

    # Print sample quick wins
    for i, qw in enumerate(quick_wins[:3], 1):
        print(f"      {i}. [{qw.get('icon', '?')}] {qw.get('title', 'No title')}")
        print(f"         {qw.get('description', 'No description')[:80]}...")

    # 6. Role-specific validations
    if validations.get("should_mention_senior_roles"):
        senior_roles_found = any("senior" in opp.lower() or "staff" in opp.lower() or "principal" in opp.lower() for opp in opportunities)
        if not senior_roles_found:
            failures.append("Expected senior/staff/principal roles but none found")
        else:
            print(f"\n   ✓ Senior/Staff roles mentioned")

    if validations.get("should_mention_devops_tools"):
        devops_tools_found = any("terraform" in tool.lower() or "kubernetes" in tool.lower() or "prometheus" in tool.lower() for tool in tools)
        if not devops_tools_found:
            failures.append("Expected DevOps tools (Terraform, Kubernetes, Prometheus) but none found")
        else:
            print(f"\n   ✓ DevOps-specific tools mentioned")

    # Final result
    passed = len(failures) == 0

    print(f"\n{'='*100}")
    if passed:
        print(f"✅ TEST PASSED")
    else:
        print(f"❌ TEST FAILED - {len(failures)} issues:")
        for failure in failures:
            print(f"   - {failure}")
    print(f"{'='*100}")

    return {
        "name": scenario["name"],
        "passed": passed,
        "failures": failures,
        "elapsed": elapsed,
        "score": score
    }


def main():
    """Run all test scenarios."""
    print("="*100)
    print("LIVE API TESTING - Profile Evaluation System")
    print("="*100)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Running {len(TEST_SCENARIOS)} test scenarios...\n")

    # Check API health
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ API is healthy and running\n")
        else:
            print(f"⚠️  API health check returned status {health_response.status_code}\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print(f"   Error: {str(e)}")
        print(f"\n   Make sure the backend is running:")
        print(f"   cd backend && python3 -m uvicorn main:app --reload --port 8000\n")
        return

    results = []
    total_time = 0

    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        result = run_test_scenario(scenario, i, len(TEST_SCENARIOS))
        results.append(result)
        total_time += result["elapsed"]

        # Add delay between tests to avoid rate limiting
        if i < len(TEST_SCENARIOS):
            print(f"\nWaiting 2 seconds before next test...")
            time.sleep(2)

    # Print summary
    print("\n\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100)

    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count

    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed_count} ({passed_count/len(results)*100:.1f}%)")
    print(f"Failed: {failed_count} ({failed_count/len(results)*100:.1f}%)")
    print(f"Total Time: {total_time:.1f}s (avg {total_time/len(results):.1f}s per test)")

    print(f"\nResults by Test:")
    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"\n{status}: {result['name']}")
        print(f"   Score: {result.get('score', 'N/A')}/100")
        print(f"   Time: {result['elapsed']:.1f}s")
        if not result["passed"]:
            print(f"   Failures:")
            for failure in result["failures"][:3]:  # Show first 3 failures
                print(f"      - {failure}")
            if len(result["failures"]) > 3:
                print(f"      ... and {len(result['failures']) - 3} more")

    print("\n" + "="*100)
    if failed_count == 0:
        print("🎉 ALL TESTS PASSED!")
    elif passed_count >= len(results) * 0.7:
        print(f"✓ MOSTLY PASSING ({passed_count}/{len(results)})")
    else:
        print(f"⚠️  {failed_count} TEST(S) FAILED - Review output above")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
