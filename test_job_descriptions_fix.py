"""
Test script to verify:
1. Seniority determination respects experience
2. Job matching is deterministic (same input → same output)
"""

from job_descriptions import _get_seniority_level, generate_job_opportunities


def test_seniority_determination():
    """Test that seniority levels are correctly determined."""
    print("\n" + "=" * 80)
    print("TEST: Seniority Determination")
    print("=" * 80)

    test_cases = [
        {
            "name": "3-5 years service company, no prep → MID (not junior)",
            "profile": {
                "experience": "3-5",
                "currentRole": "swe-service",
                "problemSolving": "11-50",  # Some prep
                "portfolio": "none"
            },
            "expected": "mid"
        },
        {
            "name": "3-5 years product company with good prep → SENIOR (strong signals)",
            "profile": {
                "experience": "3-5",
                "currentRole": "swe-product",
                "problemSolving": "51-100",
                "portfolio": "limited-1-5"
            },
            "expected": "senior"  # 51-100 problems + product company + portfolio = 4 signals → senior
        },
        {
            "name": "3-5 years product company, good prep → SENIOR",
            "profile": {
                "experience": "3-5",
                "currentRole": "swe-product",
                "problemSolving": "100+",
                "systemDesign": "once",
                "portfolio": "active-5+"
            },
            "expected": "senior"
        },
        {
            "name": "5-8 years → SENIOR (regardless of prep)",
            "profile": {
                "experience": "5-8",
                "currentRole": "swe-service",
                "problemSolving": "11-50",
                "systemDesign": "not-yet",
                "portfolio": "none"
            },
            "expected": "senior"
        },
        {
            "name": "8+ years → SENIOR (regardless of prep)",
            "profile": {
                "experience": "8+",
                "currentRole": "swe-product",
                "problemSolving": "0-10",  # Rusty
                "systemDesign": "once",
                "portfolio": "inactive"
            },
            "expected": "senior"
        },
        {
            "name": "8+ years with strong system design → STAFF",
            "profile": {
                "experience": "8+",
                "currentRole": "swe-product",
                "problemSolving": "100+",
                "systemDesign": "multiple",
                "portfolio": "active-5+"
            },
            "expected": "staff"
        },
        {
            "name": "0-2 years → JUNIOR (even with 100+ problems)",
            "profile": {
                "experience": "0-2",
                "currentRole": "swe-service",
                "problemSolving": "100+",
                "systemDesign": "not-yet",
                "portfolio": "limited-1-5"
            },
            "expected": "junior"
        },
    ]

    all_passed = True

    for test in test_cases:
        result = _get_seniority_level(test["profile"])
        passed = result == test["expected"]

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Expected: {test['expected']}, Got: {result}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL SENIORITY TESTS PASSED")
    else:
        print("❌ SOME SENIORITY TESTS FAILED")
    print("=" * 80)

    return all_passed


def test_deterministic_job_matching():
    """Test that job opportunities are deterministic."""
    print("\n" + "=" * 80)
    print("TEST: Deterministic Job Matching")
    print("=" * 80)

    profile = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "targetRole": "senior-backend",
        "targetCompany": "faang",
        "currentSkill": "backend",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+"
    }

    print("\nGenerating job opportunities 3 times with same profile...")

    # Generate 3 times
    run1 = generate_job_opportunities("tech", profile)
    run2 = generate_job_opportunities("tech", profile)
    run3 = generate_job_opportunities("tech", profile)

    # Check if all runs are identical
    if run1 == run2 == run3:
        print("✅ PASS: All 3 runs produced identical results")
        print("\nSample job opportunities:")
        for i, opp in enumerate(run1, 1):
            print(f"  {i}. {opp}")
        return True
    else:
        print("❌ FAIL: Runs produced different results")
        print(f"\nRun 1: {run1}")
        print(f"\nRun 2: {run2}")
        print(f"\nRun 3: {run3}")
        return False


def test_different_profiles_get_different_jobs():
    """Test that different profiles get different job recommendations."""
    print("\n" + "=" * 80)
    print("TEST: Different Profiles Get Different Jobs")
    print("=" * 80)

    profile1 = {
        "experience": "3-5",
        "currentRole": "swe-product",
        "targetRole": "backend-sde",
        "targetCompany": "unicorns",
        "currentSkill": "backend",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "limited-1-5"
    }

    profile2 = {
        "experience": "8+",
        "currentRole": "swe-product",
        "targetRole": "senior-fullstack",
        "targetCompany": "faang",
        "currentSkill": "fullstack",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+"
    }

    jobs1 = generate_job_opportunities("tech", profile1)
    jobs2 = generate_job_opportunities("tech", profile2)

    # Check seniority levels
    seniority1 = _get_seniority_level(profile1)
    seniority2 = _get_seniority_level(profile2)

    print(f"\nProfile 1 Seniority: {seniority1}")
    print(f"Profile 2 Seniority: {seniority2}")

    print(f"\nProfile 1 Jobs:")
    for i, opp in enumerate(jobs1, 1):
        print(f"  {i}. {opp}")

    print(f"\nProfile 2 Jobs:")
    for i, opp in enumerate(jobs2, 1):
        print(f"  {i}. {opp}")

    # Verify jobs are different (they have different seniority levels)
    if jobs1 != jobs2:
        print("\n✅ PASS: Different profiles get different job recommendations")
        return True
    else:
        print("\n❌ FAIL: Different profiles got same job recommendations")
        return False


def main():
    print("\n" + "#" * 80)
    print("# JOB DESCRIPTIONS LOGIC TEST SUITE")
    print("#" * 80)

    # Run all tests
    test1_passed = test_seniority_determination()
    test2_passed = test_deterministic_job_matching()
    test3_passed = test_different_profiles_get_different_jobs()

    # Final summary
    print("\n" + "#" * 80)
    print("# TEST SUITE SUMMARY")
    print("#" * 80)

    if test1_passed and test2_passed and test3_passed:
        print("✅ ALL TESTS PASSED")
        print("\nKey Improvements:")
        print("  - 3-5 years now default to MID-LEVEL (respects experience)")
        print("  - 5-8+ years always get SENIOR roles (regardless of prep)")
        print("  - Job matching is deterministic (same input → same output)")
    else:
        print("❌ SOME TESTS FAILED")

    print("#" * 80 + "\n")


if __name__ == "__main__":
    main()
