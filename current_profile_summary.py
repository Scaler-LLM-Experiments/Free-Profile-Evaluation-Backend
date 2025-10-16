"""
Generate detailed current profile summaries from quiz responses.

This module creates conversational, personalized summaries of the user's
current state based on their actual quiz answers. Used in the Career Transition
section to show "where you are now" before displaying timeline paths.
"""

from typing import Dict, Any


def _format_experience(experience: str) -> str:
    """Format experience for display."""
    mapping = {
        "0": "No professional experience",
        "0-2": "0-2 years of experience",
        "3-5": "3-5 years of experience",
        "5-8": "5-8 years of experience",
        "8+": "8+ years of experience"
    }
    return mapping.get(experience, "Some experience")


def _format_current_role(current_role: str) -> str:
    """Format current role for display."""
    mapping = {
        "swe-product": "Software Engineer at a Product Company",
        "swe-service": "Software Engineer at a Service Company",
        "devops": "DevOps Engineer",
        "qa-support": "QA/Support Engineer",
        "career-switcher": "Career Switcher",
        "student": "Student",
        "exploring": "Exploring Tech Careers"
    }
    return mapping.get(current_role, "Professional")


def _format_problem_solving(problem_solving: str) -> str:
    """Format problem-solving activity for display."""
    mapping = {
        "0-10": "minimal coding practice (0-10 problems solved)",
        "11-50": "some coding practice (11-50 problems solved)",
        "51-100": "moderate coding practice (51-100 problems solved)",
        "100+": "extensive coding practice (100+ problems solved)"
    }
    return mapping.get(problem_solving, "some coding practice")


def _format_system_design(system_design: str) -> str:
    """Format system design experience for display."""
    mapping = {
        "not-yet": "no system design experience",
        "learning": "learning system design concepts",
        "once": "participated in system design discussions",
        "multiple": "led multiple system design discussions"
    }
    return mapping.get(system_design, "some system design knowledge")


def _format_portfolio(portfolio: str) -> str:
    """Format portfolio for display."""
    mapping = {
        "none": "no portfolio projects",
        "inactive": "some inactive portfolio projects",
        "limited-1-5": "1-5 portfolio projects",
        "active-5+": "5+ active portfolio projects"
    }
    return mapping.get(portfolio, "some portfolio projects")


def _format_code_comfort(code_comfort: str) -> str:
    """Format code comfort level for non-tech users."""
    mapping = {
        "complete-beginner": "complete beginner with code",
        "beginner": "beginner with code",
        "learning": "learning to code",
        "confident": "confident with code"
    }
    return mapping.get(code_comfort, "learning to code")


def _format_steps_taken(steps_taken: str) -> str:
    """Format steps taken for non-tech users."""
    mapping = {
        "just-exploring": "just exploring the field",
        "self-learning": "self-learning through online resources",
        "completed-course": "completed a coding course",
        "built-projects": "built personal projects",
        "bootcamp": "attended a coding bootcamp"
    }
    return mapping.get(steps_taken, "learning")


def _format_time_per_week(time_per_week: str) -> str:
    """Format time commitment for non-tech users."""
    mapping = {
        "0-2": "0-2 hours per week",
        "3-5": "3-5 hours per week",
        "6-10": "6-10 hours per week",
        "10+": "10+ hours per week"
    }
    return mapping.get(time_per_week, "some hours per week")


def generate_current_profile_summary(
    background: str,
    quiz_responses: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed current profile summary from quiz responses.

    Args:
        background: "tech" or "non-tech"
        quiz_responses: User's quiz responses

    Returns:
        {
            "title": "Your Current Profile",
            "summary": "Conversational summary paragraph",
            "key_stats": [
                {"label": "Experience", "value": "3-5 years"},
                {"label": "Current Role", "value": "Software Engineer at Service Company"},
                ...
            ]
        }
    """
    if background == "tech":
        return _generate_tech_profile_summary(quiz_responses)
    else:
        return _generate_nontech_profile_summary(quiz_responses)


def _generate_tech_profile_summary(quiz_responses: Dict[str, Any]) -> Dict[str, Any]:
    """Generate tech background profile summary."""

    experience = quiz_responses.get("experience", "0-2")
    current_role = quiz_responses.get("currentRole", "swe-service")
    current_company = quiz_responses.get("currentCompany", "your current company")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    portfolio = quiz_responses.get("portfolio", "none")

    # SIMPLIFIED: Use labels directly from frontend when available
    current_role_label = quiz_responses.get("currentRoleLabel")

    # Build conversational summary
    exp_text = _format_experience(experience)
    # Use label if available, otherwise fall back to mapping
    role_text = current_role_label if current_role_label else _format_current_role(current_role)
    ps_text = _format_problem_solving(problem_solving)
    sd_text = _format_system_design(system_design)
    port_text = _format_portfolio(portfolio)

    # Create narrative summary
    if experience in ["0", "0-2"]:
        # Junior narrative
        summary = (
            f"You're currently a {role_text.lower()} with {exp_text.lower()}. "
            f"You have {ps_text} and {sd_text}. "
            f"Your portfolio includes {port_text}."
        )
    elif experience == "3-5":
        # Mid-level narrative
        summary = (
            f"You're a {role_text.lower()} with {exp_text.lower()} at {current_company}. "
            f"You've completed {ps_text}, {sd_text}, and have {port_text}."
        )
    else:
        # Senior narrative
        summary = (
            f"You're an experienced {role_text.lower()} with {exp_text.lower()} at {current_company}. "
            f"You have {ps_text}, {sd_text}, and maintain {port_text}."
        )

    # Build key stats
    key_stats = [
        {
            "label": "Experience",
            "value": _format_experience(experience),
            "icon": "briefcase"
        },
        {
            "label": "Current Role",
            # SIMPLIFIED: Use label directly if available
            "value": current_role_label if current_role_label else _format_current_role(current_role),
            "icon": "user"
        },
        {
            "label": "Coding Practice",
            "value": problem_solving.upper() if problem_solving in ["100+"] else f"{problem_solving} problems",
            "icon": "code"
        }
    ]

    # Add system design if relevant
    if experience not in ["0", "0-2"]:
        sd_display = {
            "not-yet": "Not Yet",
            "learning": "Learning",
            "once": "Participated",
            "multiple": "Extensive"
        }.get(system_design, "Some")

        key_stats.append({
            "label": "System Design",
            "value": sd_display,
            "icon": "layout"
        })

    # Add portfolio
    port_display = {
        "none": "None",
        "inactive": "Inactive",
        "limited-1-5": "1-5 Projects",
        "active-5+": "5+ Active Projects"
    }.get(portfolio, "Some")

    key_stats.append({
        "label": "Portfolio",
        "value": port_display,
        "icon": "folder"
    })

    return {
        "title": "Your Current Profile",
        "summary": summary,
        "key_stats": key_stats
    }


def _generate_nontech_profile_summary(quiz_responses: Dict[str, Any]) -> Dict[str, Any]:
    """Generate non-tech background profile summary."""

    experience = quiz_responses.get("experience", "0")
    current_role = quiz_responses.get("currentRole", "career-switcher")
    code_comfort = quiz_responses.get("codeComfort", "complete-beginner")
    steps_taken = quiz_responses.get("stepsTaken", "just-exploring")
    time_per_week = quiz_responses.get("timePerWeek", "0-2")

    # Build conversational summary
    comfort_text = _format_code_comfort(code_comfort)
    steps_text = _format_steps_taken(steps_taken)
    time_text = _format_time_per_week(time_per_week)

    # Create narrative summary
    if experience == "0":
        # No professional experience
        summary = (
            f"You're transitioning into tech from a non-tech background. "
            f"Currently, you're {comfort_text} and have been {steps_text}. "
            f"You're dedicating {time_text} to learning."
        )
    else:
        # Has professional experience in other field
        exp_text = _format_experience(experience)
        summary = (
            f"You have {exp_text.lower()} in non-tech roles and are transitioning to tech. "
            f"You're {comfort_text}, have been {steps_text}, and are dedicating {time_text} to upskilling."
        )

    # Build key stats
    key_stats = [
        {
            "label": "Background",
            "value": "Non-Tech Career Switcher",
            "icon": "briefcase"
        },
        {
            "label": "Code Comfort",
            "value": {
                "complete-beginner": "Complete Beginner",
                "beginner": "Beginner",
                "learning": "Learning",
                "confident": "Confident"
            }.get(code_comfort, "Learning"),
            "icon": "code"
        },
        {
            "label": "Steps Taken",
            "value": {
                "just-exploring": "Just Exploring",
                "self-learning": "Self-Learning",
                "completed-course": "Completed Course",
                "built-projects": "Built Projects",
                "bootcamp": "Attended Bootcamp"
            }.get(steps_taken, "Learning"),
            "icon": "chart-line"
        },
        {
            "label": "Time Commitment",
            "value": time_per_week.replace("-", " to ") + " hrs/week",
            "icon": "clock"
        }
    ]

    # Add experience if non-zero
    if experience != "0":
        key_stats.insert(1, {
            "label": "Prior Experience",
            "value": _format_experience(experience),
            "icon": "user"
        })

    return {
        "title": "Your Current Profile",
        "summary": summary,
        "key_stats": key_stats
    }


# Example usage for testing
if __name__ == "__main__":
    print("=" * 80)
    print("CURRENT PROFILE SUMMARY TEST CASES")
    print("=" * 80)

    # Test Case 1: Mid-level tech professional
    test_1 = {
        "experience": "3-5",
        "currentRole": "swe-service",
        "currentCompany": "TCS",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "limited-1-5"
    }
    result_1 = generate_current_profile_summary("tech", test_1)
    print(f"\nTest 1: Mid-Level Tech Professional")
    print(f"Title: {result_1['title']}")
    print(f"Summary: {result_1['summary']}")
    print(f"Key Stats:")
    for stat in result_1['key_stats']:
        print(f"  - {stat['label']}: {stat['value']}")

    # Test Case 2: Junior with gaps
    test_2 = {
        "experience": "0-2",
        "currentRole": "swe-product",
        "currentCompany": "Startup XYZ",
        "problemSolving": "11-50",
        "systemDesign": "not-yet",
        "portfolio": "none"
    }
    result_2 = generate_current_profile_summary("tech", test_2)
    print(f"\nTest 2: Junior with Gaps")
    print(f"Summary: {result_2['summary']}")
    print(f"Key Stats:")
    for stat in result_2['key_stats']:
        print(f"  - {stat['label']}: {stat['value']}")

    # Test Case 3: Senior engineer
    test_3 = {
        "experience": "8+",
        "currentRole": "swe-product",
        "currentCompany": "Google",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+"
    }
    result_3 = generate_current_profile_summary("tech", test_3)
    print(f"\nTest 3: Senior Engineer")
    print(f"Summary: {result_3['summary']}")

    # Test Case 4: Non-tech career switcher
    test_4 = {
        "experience": "5+",
        "currentRole": "career-switcher",
        "codeComfort": "learning",
        "stepsTaken": "completed-course",
        "timePerWeek": "10+"
    }
    result_4 = generate_current_profile_summary("non-tech", test_4)
    print(f"\nTest 4: Non-Tech Career Switcher")
    print(f"Summary: {result_4['summary']}")
    print(f"Key Stats:")
    for stat in result_4['key_stats']:
        print(f"  - {stat['label']}: {stat['value']}")

    # Test Case 5: Complete beginner
    test_5 = {
        "experience": "0",
        "currentRole": "student",
        "codeComfort": "complete-beginner",
        "stepsTaken": "just-exploring",
        "timePerWeek": "3-5"
    }
    result_5 = generate_current_profile_summary("non-tech", test_5)
    print(f"\nTest 5: Complete Beginner")
    print(f"Summary: {result_5['summary']}")

    print("\n" + "=" * 80)
