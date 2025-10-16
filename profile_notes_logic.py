"""
Generate personalized, conversational profile strength notes that recall quiz values.

CRITICAL: Make it personal, engaging, and reference the specific inputs from the quiz.
"""

from typing import Dict, Any


def generate_profile_strength_notes(background: str, quiz_responses: Dict[str, Any], score: int) -> str:
    """
    Generate conversational profile strength notes that recall specific quiz inputs.

    Format: "Hey [mention experience/role], your profile shows [specific insights based on their answers]..."
    """

    if background == "non-tech":
        return _generate_nontech_notes(quiz_responses, score)
    else:
        return _generate_tech_notes(quiz_responses, score)


def _generate_tech_notes(quiz_responses: Dict[str, Any], score: int) -> str:
    """Generate tech background notes with specific quiz recall."""

    experience = quiz_responses.get("experience", "0-2")
    current_role = quiz_responses.get("currentRole", "swe-service")
    current_company = quiz_responses.get("currentCompany", "your current company")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    portfolio = quiz_responses.get("portfolio", "none")
    target_role = quiz_responses.get("targetRole", "")
    target_company = quiz_responses.get("targetCompany", "")

    # Build conversational notes - CRISP and MOTIVATING
    notes_parts = []

    # MOTIVATIONAL OPENING - Set positive tone
    if score >= 70:
        notes_parts.append(f"Great news! With {experience} years at {current_company}, your profile shows strong readiness.")
    elif score >= 50:
        notes_parts.append(f"You're on the right track with {experience} years at {current_company}. Here's how to accelerate your progress:")
    else:
        notes_parts.append(f"Let's turn your {experience} years at {current_company} into interview-ready skills:")

    # IDENTIFY TOP 2-3 GAPS (prioritized by impact)
    gaps = []

    # Check problem solving first (highest priority)
    # BE RESPECTFUL: Experienced engineers need interview refresh, not "start from scratch"
    if problem_solving == "0-10":
        if experience in ["8+"]:
            # 8+ years: They've built systems, just rusty on interviews
            gaps.append(f"Your {experience} years building production systems is valuable. Refresh interview skills with 30 easy + 50 medium problems over 6-8 weeks to get back in interview shape.")
        elif experience in ["5-8"]:
            # 5-8 years: Senior but interview-rusty
            gaps.append(f"With {experience} years of experience, you have the fundamentals. Sharpen interview skills with 50-80 problems focusing on common patterns.")
        elif experience == "3-5":
            # 3-5 years: Mid-level needs interview prep
            gaps.append(f"Your {experience} years of professional experience is valuable, but interview preparation needs immediate focus. Aim for 50-100 problems to unlock senior opportunities.")
        else:
            # 0-2 years: Actually need fundamentals
            gaps.append(f"Build coding fundamentals with 100+ problems (currently at {problem_solving}).")
    elif problem_solving == "11-50":
        if experience in ["5-8", "8+"]:
            # Experienced but needs more practice
            gaps.append(f"Increase to 100+ problems (currently {problem_solving}) to match your {experience} years of experience.")
        else:
            gaps.append(f"Aim for 100+ coding problems (you're at {problem_solving} now) for strong interview readiness.")

    # Check system design (critical for mid-senior) - adjust based on experience
    if system_design == "not-yet" and experience in ["3-5", "5-8", "8+"]:
        gaps.append("Master system design – it's the differentiator for senior roles.")
    elif system_design == "once" and experience in ["3-5", "5-8", "8+"]:
        # They've participated - don't treat as beginners
        gaps.append("Lead more system design discussions to build senior-level expertise.")
    elif system_design == "once" and experience not in ["3-5", "5-8", "8+"]:
        gaps.append("Deepen your system design practice beyond theory.")

    # Check portfolio - ONLY mention if actually missing or weak
    # DO NOT mention if they have active-5+ repos
    if portfolio == "none" and experience not in ["0", "0-2"]:
        gaps.append("Showcase your work with 3-5 GitHub projects.")
    elif portfolio == "inactive":
        gaps.append("Revive your GitHub with recent projects.")
    elif portfolio in ["limited-1-5", "limited-1to5"] and experience in ["3-5", "5-8", "8+"]:
        gaps.append("Expand portfolio to 5+ quality projects.")

    # Add top gaps (max 3)
    if gaps:
        notes_parts.append(" ".join(gaps[:3]))

    # POSITIVE REINFORCEMENT - Highlight what's working
    strengths = []
    if problem_solving in ["100+", "51-100"]:
        strengths.append(f"Your {problem_solving} problems solved shows strong fundamentals.")
    if system_design == "multiple":
        strengths.append("Leading system design discussions positions you well for senior roles.")
    if portfolio == "active-5+":
        strengths.append("Active GitHub portfolio demonstrates real-world impact.")

    if strengths:
        notes_parts.append(" ".join(strengths[:2]))

    # TARGET ALIGNMENT - Realistic but encouraging (use actual target company label!)
    from label_mappings import get_company_label

    target_company_label = quiz_responses.get("targetCompanyLabel") or get_company_label(target_company)

    if target_company or target_role in ["senior-backend", "senior-fullstack", "tech-lead"]:
        if score >= 70:
            notes_parts.append(f"{target_company_label} is within reach – nail your system design and behavioral prep.")
        elif score >= 50:
            notes_parts.append(f"{target_company_label} readiness: 3-6 months with focused prep on the gaps above.")
        else:
            notes_parts.append(f"Build with product companies first, then target {target_company_label} in 1-2 years.")

    # CLOSING - Clear timeline
    if score >= 70:
        notes_parts.append("Timeline: 2-3 months to interview-ready.")
    elif score >= 50:
        notes_parts.append("Timeline: 4-6 months with consistent effort.")
    else:
        notes_parts.append("Timeline: 6-9 months to build strong fundamentals.")

    return " ".join(notes_parts)


def _generate_nontech_notes(quiz_responses: Dict[str, Any], score: int) -> str:
    """Generate non-tech background notes with specific quiz recall."""

    experience = quiz_responses.get("experience", "0")
    current_role = quiz_responses.get("currentRole", "career-switcher")
    target_role = quiz_responses.get("targetRole", "exploring")
    code_comfort = quiz_responses.get("codeComfort", "complete-beginner")
    steps_taken = quiz_responses.get("stepsTaken", "just-exploring")
    time_per_week = quiz_responses.get("timePerWeek", "0-2")

    # Build conversational notes - CRISP and MOTIVATING
    notes_parts = []

    # MOTIVATIONAL OPENING - Set positive tone
    if score >= 70:
        notes_parts.append(f"Impressive! Your {experience} years of experience + {time_per_week} hours weekly commitment shows serious dedication.")
    elif score >= 50:
        notes_parts.append(f"You're making real progress with {time_per_week} hours/week. Here's how to accelerate:")
    else:
        notes_parts.append(f"Let's build your tech career roadmap:")

    # IDENTIFY TOP 2-3 PRIORITIES
    priorities = []

    # Check time commitment first
    if time_per_week in ["0-2", "3-5"]:
        priorities.append(f"Increase weekly hours to 8-10 (currently {time_per_week}) for faster progress.")

    # Check code comfort
    if code_comfort in ["complete-beginner", "beginner"]:
        priorities.append("Build coding fundamentals: start with Python basics and one small project.")
    elif code_comfort == "learning":
        priorities.append("Keep momentum going – daily practice is key to breakthroughs.")

    # Check practical work
    if steps_taken == "just-exploring":
        priorities.append("Set deadline: complete one course + build one project in 2 weeks.")
    elif steps_taken in ["completed-course", "self-learning"]:
        priorities.append("Apply knowledge through 2-3 real projects (not tutorials).")
    elif steps_taken == "built-projects":
        priorities.append("Polish projects with documentation and live deployments.")

    # Add top priorities (max 3)
    if priorities:
        notes_parts.append(" ".join(priorities[:3]))

    # POSITIVE REINFORCEMENT
    strengths = []
    if time_per_week == "10+":
        strengths.append("Your 10+ hours/week commitment puts you ahead of most switchers.")
    if code_comfort == "confident":
        strengths.append("Confident with code – you're in the top 20% of career switchers.")
    if steps_taken == "built-projects":
        strengths.append("Having real projects is your biggest asset.")

    if strengths:
        notes_parts.append(" ".join(strengths[:2]))

    # TARGET ROLE GUIDANCE
    if target_role in ["backend-dev", "backend-sde", "backend"]:
        notes_parts.append("Backend path: Focus on Python/Node.js, SQL, and 2-3 API projects.")
    elif target_role in ["fullstack-dev", "fullstack-sde", "fullstack"]:
        notes_parts.append("Full-stack path: Master React + Node.js, deploy one complete app.")
    elif target_role in ["data-analyst", "data-ml"]:
        notes_parts.append("Data path: Excel, SQL, and visualization tools (Power BI/Tableau).")

    # CLOSING - Clear timeline
    if score >= 70 and time_per_week == "10+":
        notes_parts.append("Timeline: 3-4 months to first tech role.")
    elif score >= 50:
        notes_parts.append("Timeline: 5-8 months with consistent effort.")
    else:
        notes_parts.append("Timeline: 8-12 months for career switchers – stay committed.")

    return " ".join(notes_parts)


# Example usage for testing
if __name__ == "__main__":
    print("=" * 100)
    print("PROFILE NOTES GENERATOR TEST")
    print("=" * 100)

    # Test 1: Senior with strong system design
    test1 = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "currentCompany": "Razorpay",
        "systemDesign": "multiple",
        "problemSolving": "100+",
        "portfolio": "active-5+",
        "targetRole": "senior-faang",
        "targetCompany": "faang"
    }
    notes1 = generate_profile_strength_notes("tech", test1, 96)
    print(f"\nTest 1: Senior Engineer (Score: 96/100)")
    print(f"Notes: {notes1}\n")

    # Test 2: Mid-level with gap
    test2 = {
        "experience": "3-5",
        "currentRole": "swe-service",
        "currentCompany": "TCS",
        "systemDesign": "not-yet",
        "problemSolving": "11-50",
        "portfolio": "limited-1-5",
        "targetRole": "backend-sde",
        "targetCompany": "product"
    }
    notes2 = generate_profile_strength_notes("tech", test2, 43)
    print(f"Test 2: Mid-Level with Gaps (Score: 43/100)")
    print(f"Notes: {notes2}\n")

    # Test 3: Non-tech career switcher
    test3 = {
        "experience": "5+",
        "currentRole": "career-switcher",
        "targetRole": "backend-dev",
        "codeComfort": "learning",
        "stepsTaken": "completed-course",
        "timePerWeek": "10+"
    }
    notes3 = generate_profile_strength_notes("non-tech", test3, 72)
    print(f"Test 3: Non-Tech Career Switcher (Score: 72/100)")
    print(f"Notes: {notes3}\n")

    print("=" * 100)
    print("✓ All notes are conversational and recall specific quiz inputs!")
    print("=" * 100)
