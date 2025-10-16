#!/usr/bin/env python3
"""
Test to verify:
1. ALL scores are >= 45%
2. NO scores are multiples of 5 (no 45%, 50%, 55%, 60%, etc.)

This test creates 20+ different profile combinations to validate requirements.
"""

from scoring_logic import calculate_profile_strength

def test_score_requirements():
    """Test that all scores meet requirements: >= 45% and NOT multiples of 5"""

    test_profiles = []

    # Tech profiles - various combinations
    tech_experiences = ["0-2", "3-5", "5-8", "8+"]
    tech_roles = ["swe-product", "swe-service", "devops", "qa-support"]
    tech_sd = ["not-yet", "learning", "once", "multiple"]
    tech_ps = ["0-10", "11-50", "51-100", "100+"]
    tech_portfolio = ["none", "inactive", "limited-1-5", "active-5+"]

    # Create diverse tech profiles
    import itertools
    for exp, role, sd, ps, port in itertools.product(
        ["0-2", "3-5", "5-8"],
        ["swe-product", "swe-service"],
        ["not-yet", "multiple"],
        ["0-10", "100+"],
        ["none", "active-5+"]
    ):
        test_profiles.append(("tech", {
            "experience": exp,
            "currentRole": role,
            "systemDesign": sd,
            "problemSolving": ps,
            "portfolio": port
        }))

    # Non-tech profiles - various combinations
    nontech_experiences = ["0", "0-2", "3-5", "5+"]
    nontech_comfort = ["complete-beginner", "beginner", "learning", "confident"]
    nontech_steps = ["just-exploring", "self-learning", "completed-course", "built-projects"]
    nontech_time = ["0-2", "3-5", "6-10", "10+"]

    # Create diverse non-tech profiles
    for exp, comfort, steps, time in itertools.product(
        ["0", "3-5", "5+"],
        ["complete-beginner", "confident"],
        ["just-exploring", "built-projects"],
        ["0-2", "10+"]
    ):
        test_profiles.append(("non-tech", {
            "experience": exp,
            "codeComfort": comfort,
            "stepsTaken": steps,
            "timePerWeek": time
        }))

    print("=" * 100)
    print(f"TESTING {len(test_profiles)} DIFFERENT PROFILES")
    print("=" * 100)
    print("\nRequirements:")
    print("✓ ALL scores must be >= 45%")
    print("✓ NO scores can be multiples of 5 (no 45%, 50%, 55%, 60%, etc.)")
    print("\n" + "=" * 100)

    failures = []
    all_scores = []

    for idx, (background, quiz) in enumerate(test_profiles, 1):
        result = calculate_profile_strength(background, quiz)
        score = result["score"]
        all_scores.append(score)

        # Check requirements
        is_below_45 = score < 45
        is_multiple_of_5 = score % 5 == 0

        status = "✓"
        issue = ""

        if is_below_45:
            status = "✗"
            issue = f"BELOW 45% (score: {score})"
            failures.append(f"Profile {idx}: {issue}")

        if is_multiple_of_5:
            status = "✗"
            issue = f"MULTIPLE OF 5 (score: {score})"
            failures.append(f"Profile {idx}: {issue}")

        if issue:
            print(f"{status} Profile {idx:2d}: Score {score:3d}/100 - {issue}")
        else:
            print(f"{status} Profile {idx:2d}: Score {score:3d}/100")

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"Total profiles tested: {len(test_profiles)}")
    print(f"Minimum score: {min(all_scores)}")
    print(f"Maximum score: {max(all_scores)}")
    print(f"Score distribution: {sorted(set(all_scores))}")

    # Check for multiples of 5
    multiples_of_5 = [s for s in all_scores if s % 5 == 0]
    below_45 = [s for s in all_scores if s < 45]

    print(f"\n✓ Scores >= 45%: {len([s for s in all_scores if s >= 45])}/{len(all_scores)}")
    print(f"✓ Scores NOT multiples of 5: {len([s for s in all_scores if s % 5 != 0])}/{len(all_scores)}")

    if multiples_of_5:
        print(f"\n✗ FAILED: Found {len(multiples_of_5)} scores that are multiples of 5: {multiples_of_5}")

    if below_45:
        print(f"\n✗ FAILED: Found {len(below_45)} scores below 45%: {below_45}")

    if failures:
        print("\n" + "=" * 100)
        print("FAILURES:")
        print("=" * 100)
        for failure in failures:
            print(f"  {failure}")
        print("\n✗✗✗ TEST FAILED ✗✗✗")
        return False
    else:
        print("\n" + "=" * 100)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("=" * 100)
        print("✓ All scores are >= 45%")
        print("✓ NO scores are multiples of 5")
        return True


if __name__ == "__main__":
    success = test_score_requirements()
    exit(0 if success else 1)
