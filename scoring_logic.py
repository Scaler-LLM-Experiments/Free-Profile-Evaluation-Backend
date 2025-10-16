"""
Intelligent profile strength scoring with proper weighting.

CRITICAL INSIGHT: System design expertise >> problem solving count for senior roles.

Weighting Philosophy:
- System Design (for 5+ years): 35-40% of score
- Experience Quality: 30-35% of score
- Problem Solving: Max 15% of score (capped!)
- Portfolio: 10-15% of score
- Contradictions: -10 to -20 penalty
"""

from typing import Any, Dict, Tuple


def _ensure_no_multiple_of_five(score: int, seed: str) -> int:
    """
    Ensure score is NOT a multiple of 5 (no 30%, 45%, 60%, etc.)

    Uses deterministic adjustment based on seed to maintain consistency.
    Minimum score is 45%.
    """
    import random

    # Enforce minimum 45%
    score = max(45, min(100, score))

    # If score is a multiple of 5, adjust it
    if score % 5 == 0:
        # Use deterministic seed to decide adjustment direction
        random.seed(hash(seed))

        # Adjust by 1, 2, or 3 (never keep multiple of 5)
        adjustment = random.choice([1, 2, 3, -1, -2, -3])
        score = score + adjustment

        # Ensure still in valid range
        score = max(45, min(100, score))

        # Double-check: if still multiple of 5, force adjust by 1
        if score % 5 == 0:
            score = score + 1 if score < 100 else score - 1

    return score


def _get_experience_score(experience: str, current_role: str) -> int:
    """
    Calculate experience score (0-35 points).

    Quality matters more than quantity:
    - Product company experience worth more than service
    - DevOps/specialized roles worth more than QA/support
    """
    # Base experience points
    exp_points = {
        "0": 0,
        "0-2": 10,
        "3-5": 20,
        "5-8": 28,
        "8+": 35
    }.get(experience, 10)

    # Role quality multiplier
    role_multipliers = {
        "swe-product": 1.0,      # Product company - highest quality
        "devops": 1.0,           # Specialized - high demand (no penalty)
        "swe-service": 1.0,      # Service company - experience is experience (no penalty)
        "qa-support": 0.90,      # Support role - minor relevance gap for SWE roles
    }

    multiplier = role_multipliers.get(current_role, 0.95)
    return int(exp_points * multiplier)


def _get_system_design_score(system_design: str, experience: str, problem_solving: str) -> Tuple[int, bool]:
    """
    Calculate system design score (0-40 points for senior, 0-15 for junior).

    Returns: (score, is_contradiction)

    CRITICAL: Leading design discussions is a SENIOR-LEVEL signal.
    Cannot have this without production experience and coding skills.
    """
    is_contradiction = False

    # Contradiction check: systemDesign='multiple' requires real experience
    if system_design == "multiple":
        # Check for contradictions
        if problem_solving in ["0-10", "11-50"] or experience in ["0", "0-2"]:
            # CONTRADICTION DETECTED!
            is_contradiction = True
            # Downgrade claim - treat as "once" instead
            system_design = "once"

    # Scoring based on experience level
    experience_years = {"0": 0, "0-2": 1, "3-5": 4, "5-8": 6.5, "8+": 10}.get(experience, 1)

    if experience_years >= 5:
        # Senior track: System design is CRITICAL
        scores = {
            "multiple": 40,  # Led discussions - MASSIVE signal
            "once": 25,      # Participated - good signal
            "learning": 15,  # Self-learning - okay signal
            "not-yet": 5     # Not started - gap for senior
        }
    else:
        # Junior/Mid track: System design is nice-to-have
        scores = {
            "multiple": 15,  # Unlikely but possible for 3-5 years
            "once": 12,      # Good for mid-level
            "learning": 8,   # Shows initiative
            "not-yet": 5     # Expected for junior
        }

    return scores.get(system_design, 5), is_contradiction


def _get_problem_solving_score(problem_solving: str) -> int:
    """
    Calculate problem solving score (0-15 points MAX).

    CAPPED at 15 points because grinding LeetCode != senior engineering.
    """
    scores = {
        "100+": 15,     # Very active - max points
        "51-100": 12,   # Moderately active - good
        "11-50": 8,     # Somewhat active - okay
        "0-10": 3       # Not active - minimal
    }
    return scores.get(problem_solving, 3)


def _get_portfolio_score(portfolio: str, problem_solving: str) -> int:
    """
    Calculate portfolio score (0-15 points).

    Quality over quantity - active projects show practical skills.
    CRITICAL: Detect tutorial portfolios (repos but no problem-solving practice).
    """
    base_scores = {
        "active-5+": 15,      # Active - best signal
        "limited-1-5": 10,    # Limited - okay signal
        "inactive": 5,        # Inactive - minimal signal
        "none": 0             # No portfolio - no signal
    }
    score = base_scores.get(portfolio, 0)

    # Detect likely tutorial portfolios
    # If someone has repos but NO problem-solving practice, repos are likely tutorials/clones
    if portfolio in ["active-5+", "limited-1-5"] and problem_solving == "0-10":
        score = score // 2  # 50% penalty - likely tutorial projects, not original work

    return score


def _detect_contradictions(quiz_responses: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Detect logical contradictions in quiz responses.

    Returns: (has_contradiction, contradiction_note)
    """
    experience = quiz_responses.get("experience", "0-2")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    portfolio = quiz_responses.get("portfolio", "none")
    current_role = quiz_responses.get("currentRole", "")

    contradictions = []

    # Contradiction 1: System Design expert without coding practice
    if system_design == "multiple" and problem_solving in ["0-10", "11-50"]:
        contradictions.append(
            "System design expertise requires extensive coding practice. "
            "Focus on solving 100+ problems to match your claimed design experience."
        )

    # Contradiction 2: Experienced engineers without interview prep
    if experience in ["3-5", "5-8", "8+"] and problem_solving == "0-10":
        if experience == "3-5":
            # Mid-level: acknowledge experience but flag interview gap
            contradictions.append(
                "Your 3-5 years of professional experience is valuable, but interview preparation "
                "needs immediate focus to unlock senior opportunities. Aim for 100+ problems."
            )
        else:
            # Senior: stronger contradiction message
            contradictions.append(
                "Your experience level doesn't match current interview readiness. "
                "Results may not reflect actual capability without practice."
            )

    # Contradiction 3: Active portfolio but no problem solving
    if portfolio == "active-5+" and problem_solving == "0-10":
        contradictions.append(
            "Your projects suggest practical experience, but lack of problem-solving practice "
            "may hinder technical interviews. Balance portfolio work with DSA prep."
        )

    # Contradiction 4: Claiming senior skills without experience
    if experience in ["0", "0-2"] and system_design == "multiple":
        contradictions.append(
            "System design expertise typically requires 5+ years of production experience. "
            "Your claim may be aspirational - focus on building fundamentals first."
        )

    if contradictions:
        return True, " ".join(contradictions)

    return False, ""


def calculate_profile_strength(background: str, quiz_responses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate profile strength score with intelligent weighting.

    Returns:
        {
            "score": 0-100,
            "has_contradictions": bool,
            "contradiction_note": str,
            "breakdown": {
                "experience": 0-35,
                "system_design": 0-40,
                "problem_solving": 0-15,
                "portfolio": 0-15
            }
        }
    """
    if background == "non-tech":
        # Non-tech scoring is different - more lenient
        return _calculate_nontech_score(quiz_responses)

    # Extract quiz responses
    experience = quiz_responses.get("experience", "0-2")
    current_role = quiz_responses.get("currentRole", "swe-service")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    portfolio = quiz_responses.get("portfolio", "none")

    # Calculate component scores
    exp_score = _get_experience_score(experience, current_role)
    sd_score, sd_contradiction = _get_system_design_score(system_design, experience, problem_solving)
    ps_score = _get_problem_solving_score(problem_solving)
    port_score = _get_portfolio_score(portfolio, problem_solving)  # Pass problem_solving to detect tutorials

    # Detect all contradictions
    has_contradictions, contradiction_note = _detect_contradictions(quiz_responses)

    # Calculate total (before penalty)
    base_score = exp_score + sd_score + ps_score + port_score

    # Apply contradiction penalty
    contradiction_penalty = 0
    if has_contradictions:
        contradiction_penalty = 15  # -15 points for contradictions

    # Final score (before variation)
    final_score = max(0, min(100, base_score - contradiction_penalty))

    # Add natural variation to avoid round numbers (makes scores more believable)
    import random
    seed_string = f"{experience}_{current_role}_{system_design}_{problem_solving}_{portfolio}"
    random.seed(hash(seed_string))
    variation = random.randint(-2, 2)
    final_score = final_score + variation

    # CRITICAL: Ensure minimum 45% and NO multiples of 5 (30%, 45%, 60% forbidden!)
    final_score = _ensure_no_multiple_of_five(final_score, seed_string)

    return {
        "score": final_score,
        "has_contradictions": has_contradictions,
        "contradiction_note": contradiction_note,
        "breakdown": {
            "experience": exp_score,
            "system_design": sd_score,
            "problem_solving": ps_score,
            "portfolio": port_score,
            "contradiction_penalty": -contradiction_penalty if contradiction_penalty > 0 else 0
        }
    }


def _calculate_nontech_score(quiz_responses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate score for non-tech background (more lenient).

    Focus on:
    - Time commitment
    - Code comfort level
    - Steps already taken
    """
    experience = quiz_responses.get("experience", "0")
    code_comfort = quiz_responses.get("codeComfort", "complete-beginner")
    steps_taken = quiz_responses.get("stepsTaken", "just-exploring")
    time_per_week = quiz_responses.get("timePerWeek", "0-2")

    # Code comfort (0-40 points) - most important for career switchers
    comfort_scores = {
        "confident": 40,
        "learning": 30,
        "beginner": 20,
        "complete-beginner": 10
    }
    comfort_score = comfort_scores.get(code_comfort, 10)

    # Steps taken (0-25 points)
    steps_scores = {
        "completed-course": 25,
        "built-projects": 25,
        "bootcamp": 20,
        "self-learning": 15,
        "just-exploring": 5
    }
    steps_score = steps_scores.get(steps_taken, 5)

    # Time commitment (0-20 points)
    time_scores = {
        "10+": 20,
        "6-10": 15,
        "3-5": 10,
        "0-2": 3
    }
    time_score = time_scores.get(time_per_week, 3)

    # Prior experience bonus (0-15 points)
    exp_scores = {
        "5+": 15,
        "3-5": 12,
        "0-2": 8,
        "0": 5
    }
    exp_score = exp_scores.get(experience, 5)

    # Total score (before variation)
    total = comfort_score + steps_score + time_score + exp_score

    # Add natural variation to avoid round numbers (makes scores more believable)
    import random
    seed_string = f"{experience}_{code_comfort}_{steps_taken}_{time_per_week}"
    random.seed(hash(seed_string))
    variation = random.randint(-2, 2)
    final_score = total + variation

    # CRITICAL: Ensure minimum 45% and NO multiples of 5 (30%, 45%, 60% forbidden!)
    final_score = _ensure_no_multiple_of_five(final_score, seed_string)

    return {
        "score": final_score,
        "has_contradictions": False,
        "contradiction_note": "",
        "breakdown": {
            "code_comfort": comfort_score,
            "steps_taken": steps_score,
            "time_commitment": time_score,
            "experience": exp_score
        }
    }


# Example usage for testing
if __name__ == "__main__":
    print("=" * 80)
    print("SCORING LOGIC TEST CASES")
    print("=" * 80)

    # Test Case 1: Senior with strong system design (should score HIGH)
    test_1 = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "systemDesign": "multiple",
        "problemSolving": "100+",
        "portfolio": "active-5+"
    }
    result_1 = calculate_profile_strength("tech", test_1)
    print(f"\nTest 1: Senior Engineer with Strong System Design")
    print(f"Score: {result_1['score']}/100")
    print(f"Breakdown: {result_1['breakdown']}")
    print(f"Contradictions: {result_1['has_contradictions']}")

    # Test Case 2: Contradictory profile (system design expert without coding)
    test_2 = {
        "experience": "3-5",
        "currentRole": "swe-service",
        "systemDesign": "multiple",  # Claims expertise
        "problemSolving": "0-10",    # But doesn't practice!
        "portfolio": "none"
    }
    result_2 = calculate_profile_strength("tech", test_2)
    print(f"\nTest 2: Contradictory Profile (SD expert without coding)")
    print(f"Score: {result_2['score']}/100")
    print(f"Breakdown: {result_2['breakdown']}")
    print(f"Contradictions: {result_2['has_contradictions']}")
    print(f"Note: {result_2['contradiction_note']}")

    # Test Case 3: Junior with realistic profile
    test_3 = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "systemDesign": "not-yet",
        "problemSolving": "51-100",
        "portfolio": "limited-1-5"
    }
    result_3 = calculate_profile_strength("tech", test_3)
    print(f"\nTest 3: Junior Engineer with Realistic Profile")
    print(f"Score: {result_3['score']}/100")
    print(f"Breakdown: {result_3['breakdown']}")
    print(f"Contradictions: {result_3['has_contradictions']}")

    # Test Case 4: LeetCode grinder without real experience
    test_4 = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "systemDesign": "not-yet",
        "problemSolving": "100+",  # Lots of grinding
        "portfolio": "none"        # But no projects
    }
    result_4 = calculate_profile_strength("tech", test_4)
    print(f"\nTest 4: LeetCode Grinder (no real projects)")
    print(f"Score: {result_4['score']}/100")
    print(f"Breakdown: {result_4['breakdown']}")
    print(f"Contradictions: {result_4['has_contradictions']}")

    # Test Case 5: Non-tech career switcher
    test_5 = {
        "experience": "5+",
        "codeComfort": "learning",
        "stepsTaken": "completed-course",
        "timePerWeek": "10+"
    }
    result_5 = calculate_profile_strength("non-tech", test_5)
    print(f"\nTest 5: Non-Tech Career Switcher")
    print(f"Score: {result_5['score']}/100")
    print(f"Breakdown: {result_5['breakdown']}")
    print(f"Contradictions: {result_5['has_contradictions']}")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS:")
    print("=" * 80)
    print("- Test 1 (Senior + SD expert): Should score 80-95+ (HIGHEST)")
    print("- Test 2 (Contradiction): Should score 40-55 (PENALTY applied)")
    print("- Test 3 (Junior realistic): Should score 35-50 (REALISTIC)")
    print("- Test 4 (LeetCode grinder): Should score 30-40 (CAPPED - no real experience)")
    print("- Test 5 (Non-tech switcher): Should score 60-75 (GOOD commitment)")
