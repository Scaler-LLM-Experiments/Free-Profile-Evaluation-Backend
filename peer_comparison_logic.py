"""
Logic for peer comparison calculations.

Calculates:
- Peer group description based on user profile
- Potential percentile if user addresses their gaps
"""

from typing import Any, Dict
from label_mappings import get_role_label, get_company_label, get_experience_label


def _get_seniority_description(experience: str, current_role: str) -> str:
    """Get seniority description for peer group."""
    if experience in ["8+"]:
        return "Senior"
    elif experience in ["5-8"]:
        return "Mid to Senior-level"
    elif experience in ["3-5"]:
        return "Mid-level"
    elif experience in ["0-2", "0"]:
        return "Junior to Mid-level"
    return "Mid-level"


def generate_peer_group_description(background: str, quiz_responses: Dict[str, Any]) -> str:
    """
    Generate human-readable peer group description.

    Format: "{Seniority} {Role} at {Company Type}"
    Example: "Senior Backend Engineers at Big Tech firms"
    """

    if background == "non-tech":
        # Non-tech: focus on career transition stage
        code_comfort = quiz_responses.get("codeComfort", "complete-beginner")
        target_role = quiz_responses.get("targetRole", "backend")

        role_label = get_role_label(target_role)

        if code_comfort in ["confident", "learning"]:
            return f"Career switchers transitioning to {role_label} roles"
        else:
            return f"Aspiring tech professionals exploring {role_label} paths"

    # Tech background
    experience = quiz_responses.get("experience", "0-2")
    target_role = quiz_responses.get("targetRole", "backend-sde")
    target_company = quiz_responses.get("targetCompany", "")

    # Get seniority description
    seniority_desc = _get_seniority_description(experience, quiz_responses.get("currentRole", ""))

    # Get role label
    role_label = get_role_label(target_role)

    # Get company type label
    company_label = get_company_label(target_company) if target_company else "tech companies"

    return f"{seniority_desc} {role_label}s at {company_label}"


def calculate_potential_percentile(
    current_percentile: int,
    background: str,
    quiz_responses: Dict[str, Any],
    profile_score: int
) -> int:
    """
    Calculate potential percentile if user addresses their key gaps.

    Logic:
    - Start with current percentile
    - Add boost based on addressable gaps:
      * Problem solving practice: +15-20 percentile
      * System design learning: +10-15 percentile
      * Portfolio building: +10-15 percentile
      * Mock interviews: +5-10 percentile
    - Cap at 90th percentile (realistic ceiling)
    """

    potential = current_percentile

    if background == "non-tech":
        # Non-tech: bigger gaps, higher potential improvement
        code_comfort = quiz_responses.get("codeComfort", "complete-beginner")
        steps_taken = quiz_responses.get("stepsTaken", "just-exploring")

        if code_comfort in ["complete-beginner", "beginner"]:
            potential += 25  # Huge gap - can improve significantly with practice
        elif code_comfort == "learning":
            potential += 15  # Good progress - moderate improvement possible

        if steps_taken in ["just-exploring", "self-learning"]:
            potential += 10  # Haven't taken structured steps yet

    else:
        # Tech background: identify specific gaps
        problem_solving = quiz_responses.get("problemSolving", "0-10")
        system_design = quiz_responses.get("systemDesign", "not-yet")
        portfolio = quiz_responses.get("portfolio", "none")
        experience = quiz_responses.get("experience", "0-2")

        # Problem solving gap
        if problem_solving == "0-10":
            potential += 20  # Big gap - interview prep is critical
        elif problem_solving == "11-50":
            potential += 12  # Moderate gap - need more practice
        elif problem_solving == "51-100":
            potential += 5   # Small gap - nearly there

        # System design gap (only for experienced engineers)
        if experience in ["3-5", "5-8", "8+"]:
            if system_design == "not-yet":
                potential += 15  # Critical gap for senior roles
            elif system_design == "learning":
                potential += 10  # Good progress, keep going
            elif system_design == "once":
                potential += 5   # Almost there

        # Portfolio gap
        if portfolio == "none":
            potential += 10  # No portfolio - need to showcase work
        elif portfolio == "inactive":
            potential += 7   # Outdated - needs refresh
        elif portfolio == "limited-1-5":
            potential += 3   # Could add more projects

    # Cap at realistic ceiling (90th percentile)
    # Even with all gaps addressed, not everyone reaches top 10%
    potential = min(90, potential)

    # Ensure potential is at least 10-15 percentile points higher than current
    # (there's always room for improvement!)
    potential = max(potential, current_percentile + 12)

    # Final cap at 90
    potential = min(90, potential)

    return potential


# Example usage for testing
if __name__ == "__main__":
    print("=" * 80)
    print("PEER COMPARISON LOGIC TEST CASES")
    print("=" * 80)

    # Test Case 1: Senior engineer targeting FAANG
    test_1 = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "targetRole": "senior-backend",
        "targetCompany": "faang",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "active-5+"
    }
    peer_group_1 = generate_peer_group_description("tech", test_1)
    potential_1 = calculate_potential_percentile(65, "tech", test_1, 72)
    print(f"\nTest 1: Senior Engineer")
    print(f"Peer Group: {peer_group_1}")
    print(f"Current: 65th percentile → Potential: {potential_1}th percentile")

    # Test Case 2: Junior engineer with gaps
    test_2 = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "targetRole": "fullstack-sde",
        "targetCompany": "startups",
        "problemSolving": "0-10",
        "systemDesign": "not-yet",
        "portfolio": "none"
    }
    peer_group_2 = generate_peer_group_description("tech", test_2)
    potential_2 = calculate_potential_percentile(40, "tech", test_2, 48)
    print(f"\nTest 2: Junior Engineer with Gaps")
    print(f"Peer Group: {peer_group_2}")
    print(f"Current: 40th percentile → Potential: {potential_2}th percentile")

    # Test Case 3: Non-tech career switcher
    test_3 = {
        "codeComfort": "learning",
        "stepsTaken": "completed-course",
        "targetRole": "backend",
        "targetCompany": "any-tech"
    }
    peer_group_3 = generate_peer_group_description("non-tech", test_3)
    potential_3 = calculate_potential_percentile(50, "non-tech", test_3, 55)
    print(f"\nTest 3: Non-Tech Career Switcher")
    print(f"Peer Group: {peer_group_3}")
    print(f"Current: 50th percentile → Potential: {potential_3}th percentile")
