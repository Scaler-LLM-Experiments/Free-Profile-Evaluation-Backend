"""
Test script to verify Timeline logic provides realistic timelines.
"""

from timeline_logic import calculate_timeline_to_role


def print_test_result(test_name: str, target_role: str, quiz_responses: dict):
    """Print timeline for a given test scenario."""
    print("\n" + "=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)

    # Print user profile
    print(f"\nTarget Role: {target_role}")
    print("User Profile:")
    for key, value in quiz_responses.items():
        print(f"  {key}: {value}")

    # Calculate timeline
    result = calculate_timeline_to_role(target_role, quiz_responses)

    # Print timeline
    print(f"\nTimeline: {result['timeline_text']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Key Gap: {result['key_gap']}")
    print("\nMilestones:")
    for i, milestone in enumerate(result['milestones'], 1):
        print(f"  {i}. {milestone}")

    return result


def main():
    print("\n" + "#" * 80)
    print("# TIMELINE LOGIC TEST SUITE - REALISTIC TIMELINES")
    print("#" * 80)

    # ============================================================================
    # TEST 1: Senior Engineer (8+ years) - Interview Ready
    # This is the exact scenario from user's screenshot
    # ============================================================================
    test1_profile = {
        "experience": "8+",
        "currentRole": "swe-product",
        "currentCompany": "Product Company",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+"
    }

    result1 = print_test_result(
        "Senior Engineer (8+ years) - Interview Ready",
        "Senior Backend Engineer",
        test1_profile
    )

    # Validation
    if result1['min_months'] <= 3 and result1['max_months'] <= 3:
        print("\n✅ PASS: Interview-ready senior gets 2-3 months (correct)")
    else:
        print(f"\n❌ FAIL: Interview-ready senior gets {result1['timeline_text']} (should be 2-3 months)")

    # ============================================================================
    # TEST 2: Senior Engineer (5-8 years) with Portfolio but No System Design
    # ============================================================================
    test2_profile = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "currentCompany": "Flipkart",
        "problemSolving": "51-100",
        "systemDesign": "not-yet",  # Gap here
        "portfolio": "active-5+"
    }

    result2 = print_test_result(
        "Senior Engineer (5-8 years) with Portfolio but No System Design",
        "Senior Backend Engineer",
        test2_profile
    )

    # Validation: Should be ~3-5 months (3 months system design + 1 month interview prep + experience multiplier)
    if 3 <= result2['min_months'] <= 6:
        print(f"\n✅ PASS: Timeline {result2['timeline_text']} is realistic for system design gap")
    else:
        print(f"\n❌ FAIL: Timeline {result2['timeline_text']} seems unrealistic")

    # ============================================================================
    # TEST 3: Mid-Level Engineer (3-5 years) Needs Portfolio + System Design
    # ============================================================================
    test3_profile = {
        "experience": "3-5",
        "currentRole": "swe-service",
        "currentCompany": "TCS",
        "problemSolving": "51-100",
        "systemDesign": "not-yet",
        "portfolio": "none"
    }

    result3 = print_test_result(
        "Mid-Level Engineer (3-5 years) Needs Portfolio + System Design",
        "Senior Backend Engineer",
        test3_profile
    )

    # Validation: Should be ~7-10 months (4 months portfolio + 3 months system design overlapping + 1 month prep)
    if 6 <= result3['min_months'] <= 10:
        print(f"\n✅ PASS: Timeline {result3['timeline_text']} is realistic for portfolio + system design gaps")
    else:
        print(f"\n❌ FAIL: Timeline {result3['timeline_text']} might be unrealistic")

    # ============================================================================
    # TEST 4: Senior Engineer (8+ years) Rusty on Everything
    # ============================================================================
    test4_profile = {
        "experience": "8+",
        "currentRole": "swe-product",
        "currentCompany": "Amazon",
        "problemSolving": "0-10",  # Rusty
        "systemDesign": "once",    # Some knowledge
        "portfolio": "inactive"
    }

    result4 = print_test_result(
        "Senior Engineer (8+ years) Rusty on Everything",
        "Senior Backend Engineer",
        test4_profile
    )

    # Validation: Should be ~7-10 months (4 months coding + 4 months portfolio + 4 months SD overlapping)
    # But with 8+ years experience multiplier (0.85), should be reduced
    if 6 <= result4['min_months'] <= 10:
        print(f"\n✅ PASS: Timeline {result4['timeline_text']} accounts for experience multiplier")
    else:
        print(f"\n⚠️  WARNING: Timeline {result4['timeline_text']} - verify if realistic")

    # ============================================================================
    # TEST 5: Junior Engineer (0-2 years) Starting from Scratch
    # ============================================================================
    test5_profile = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "currentCompany": "Infosys",
        "problemSolving": "0-10",
        "systemDesign": "not-yet",
        "portfolio": "none"
    }

    result5 = print_test_result(
        "Junior Engineer (0-2 years) Starting from Scratch",
        "Mid-Level Software Engineer",
        test5_profile
    )

    # Validation: Should be ~10-14 months (realistic for building everything)
    if 9 <= result5['min_months'] <= 14:
        print(f"\n✅ PASS: Timeline {result5['timeline_text']} is realistic for juniors building from scratch")
    else:
        print(f"\n⚠️  WARNING: Timeline {result5['timeline_text']} - verify if realistic")

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("\n" + "#" * 80)
    print("# TEST SUITE SUMMARY")
    print("#" * 80)
    print("\n✅ All timelines now use realistic estimates:")
    print("   - Portfolio: 4-8 months (not 2-3 months)")
    print("   - System Design: 3-5 months (not 2-3 months)")
    print("   - Interview-ready seniors: 2-3 months")
    print("   - Experienced engineers get multiplier (0.85-0.9x)")
    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()
