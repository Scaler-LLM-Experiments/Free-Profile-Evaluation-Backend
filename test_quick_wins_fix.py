"""
Test script to verify Quick Wins logic correctly respects seniority and existing skills.
"""

from quick_wins_logic import generate_quick_wins


def print_test_result(test_name: str, quiz_responses: dict, background: str = "tech"):
    """Print quick wins for a given test scenario."""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    # Print user profile
    print("\nUser Profile:")
    for key, value in quiz_responses.items():
        print(f"  {key}: {value}")

    # Generate quick wins
    quick_wins = generate_quick_wins(background, quiz_responses)

    # Print quick wins
    print(f"\nGenerated Quick Wins ({len(quick_wins)} items):")
    for i, win in enumerate(quick_wins, 1):
        print(f"\n{i}. {win['title']}")
        print(f"   {win['description']}")
        print(f"   Icon: {win['icon']}")

    return quick_wins


def validate_no_generic_advice_for_seniors(quick_wins: list, test_name: str):
    """Validate that seniors don't get generic advice."""
    bad_titles = [
        "build github presence",
        "start system design prep",
        "learn system design basics",
        "build one strong project",
        "practice coding regularly"
    ]

    issues = []
    for win in quick_wins:
        title_lower = win['title'].lower()
        for bad_title in bad_titles:
            if bad_title in title_lower:
                issues.append(f"❌ FAIL: Found generic recommendation '{win['title']}'")

    if issues:
        print(f"\n{'='*80}")
        print(f"VALIDATION FAILED for {test_name}:")
        for issue in issues:
            print(issue)
        print("="*80)
        return False
    else:
        print(f"\n{'='*80}")
        print(f"✅ VALIDATION PASSED for {test_name}: No generic recommendations found")
        print("="*80)
        return True


def main():
    print("\n" + "#" * 80)
    print("# QUICK WINS LOGIC TEST SUITE")
    print("#" * 80)

    all_passed = True

    # ============================================================================
    # TEST 1: Senior Engineer (8+ years) with Strong Skills
    # ============================================================================
    test1_profile = {
        "experience": "8+",
        "currentRole": "swe-product",
        "currentCompany": "Razorpay",
        "targetRole": "senior-backend",
        "targetCompany": "faang",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+",
        "mockInterviews": "5+"
    }

    wins1 = print_test_result(
        "Senior Engineer (8+ years, strong skills)",
        test1_profile
    )

    # Validate: Should NOT get generic advice
    passed1 = validate_no_generic_advice_for_seniors(wins1, "Test 1")
    all_passed = all_passed and passed1

    # Validate: SHOULD get senior-specific advice
    senior_advice = ["leadership", "mock", "company", "behavioral", "star"]
    found_senior_advice = any(
        any(keyword in win['title'].lower() or keyword in win['description'].lower()
            for keyword in senior_advice)
        for win in wins1
    )
    if found_senior_advice:
        print("✅ Found senior-specific advice (leadership/mock interviews/company research)")
    else:
        print("⚠️  WARNING: No senior-specific advice found")
        all_passed = False

    # ============================================================================
    # TEST 2: Senior Engineer (8+ years) BUT Rusty on Interview Prep
    # ============================================================================
    test2_profile = {
        "experience": "8+",
        "currentRole": "swe-product",
        "currentCompany": "Amazon",
        "targetRole": "senior-fullstack",
        "targetCompany": "faang",
        "problemSolving": "0-10",  # ❗ Rusty on coding
        "systemDesign": "multiple",
        "portfolio": "active-5+",
        "mockInterviews": "0"
    }

    wins2 = print_test_result(
        "Senior Engineer (8+ years, rusty on interview prep)",
        test2_profile
    )

    # Validate: Should get respectful messaging
    refresh_found = any(
        "refresh" in win['title'].lower() or "sharpen" in win['title'].lower()
        for win in wins2
    )
    if refresh_found:
        print("✅ Found respectful messaging (refresh/sharpen, not 'build foundation')")
    else:
        print("❌ FAIL: Should suggest 'refresh' for experienced engineers")
        all_passed = False

    # Validate: Should NOT suggest building portfolio or learning system design
    passed2 = validate_no_generic_advice_for_seniors(wins2, "Test 2")
    all_passed = all_passed and passed2

    # ============================================================================
    # TEST 3: Mid-Level Engineer (3-5 years) with Moderate Skills
    # ============================================================================
    test3_profile = {
        "experience": "3-5",
        "currentRole": "swe-service",
        "currentCompany": "TCS",
        "targetRole": "backend-sde",
        "targetCompany": "product",
        "problemSolving": "11-50",
        "systemDesign": "not-yet",
        "portfolio": "limited-1-5",
        "mockInterviews": "0"
    }

    wins3 = print_test_result(
        "Mid-Level Engineer (3-5 years, moderate skills)",
        test3_profile
    )

    # Validate: Should get system design recommendation (they haven't started)
    system_design_found = any(
        "system design" in win['title'].lower() or "system design" in win['description'].lower()
        for win in wins3
    )
    if system_design_found:
        print("✅ Found system design recommendation (appropriate for not-yet)")
    else:
        print("⚠️  WARNING: Should recommend system design for 'not-yet' level")

    # ============================================================================
    # TEST 4: Junior Engineer (0-2 years) - Should Get Foundational Advice
    # ============================================================================
    test4_profile = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "currentCompany": "Infosys",
        "targetRole": "backend-dev",
        "targetCompany": "product",
        "problemSolving": "0-10",
        "systemDesign": "not-yet",
        "portfolio": "none",
        "mockInterviews": "0"
    }

    wins4 = print_test_result(
        "Junior Engineer (0-2 years, needs foundation)",
        test4_profile
    )

    # Validate: SHOULD get foundational advice (appropriate for juniors)
    foundational_keywords = ["build", "foundation", "basic", "start"]
    found_foundational = any(
        any(keyword in win['title'].lower() for keyword in foundational_keywords)
        for win in wins4
    )
    if found_foundational:
        print("✅ Found foundational advice (appropriate for juniors)")
    else:
        print("⚠️  WARNING: Juniors should get foundational advice")

    # ============================================================================
    # TEST 5: Senior with Portfolio but No System Design
    # ============================================================================
    test5_profile = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "currentCompany": "Flipkart",
        "targetRole": "senior-backend",
        "targetCompany": "product",
        "problemSolving": "51-100",
        "systemDesign": "not-yet",  # ❗ Gap here
        "portfolio": "active-5+",
        "mockInterviews": "1-5"
    }

    wins5 = print_test_result(
        "Senior Engineer (5-8 years) with portfolio but no system design",
        test5_profile
    )

    # Validate: Should recommend system design (real gap)
    system_design_found = any(
        "system design" in win['title'].lower()
        for win in wins5
    )
    if system_design_found:
        print("✅ Correctly identifies system design gap for senior")
    else:
        print("⚠️  WARNING: Should recommend system design for seniors without it")

    # Validate: Should NOT recommend building portfolio (they already have it)
    portfolio_build = any(
        "github presence" in win['title'].lower() or "build" in win['title'].lower() and "portfolio" in win['description'].lower()
        for win in wins5
    )
    if not portfolio_build:
        print("✅ Does not recommend building portfolio (they already have active-5+)")
    else:
        print("❌ FAIL: Should not recommend building portfolio when user has active-5+")
        all_passed = False

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("\n" + "#" * 80)
    print("# TEST SUITE SUMMARY")
    print("#" * 80)

    if all_passed:
        print("✅ ALL TESTS PASSED - Quick wins logic correctly respects seniority!")
    else:
        print("❌ SOME TESTS FAILED - Review issues above")

    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()
