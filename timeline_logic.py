"""
Timeline calculation logic for career transition paths.

Calculates realistic timelines to achieve target roles based on:
- Current skill gaps
- Experience level
- Problem-solving practice
- System design expertise
- Portfolio quality

Key Principles:
- System design requires coding foundation first (can't learn in parallel)
- Portfolio projects require coding skills
- Experience level affects learning speed
- Multiple gaps require sequential work, single gaps can be accelerated
"""

from typing import Dict, List, Tuple, Any


def _calculate_coding_gap_months(problem_solving: str, target_level: str) -> int:
    """
    Calculate months needed to close coding gap.

    Args:
        problem_solving: Current level ("0-10", "11-50", "51-100", "100+")
        target_level: Required level for target role ("junior", "mid", "senior")

    Returns:
        Months needed (0 if no gap)
    """
    # Define requirements by target level
    requirements = {
        "junior": "51-100",      # Need decent foundation
        "mid": "100+",           # Need strong interview skills
        "senior": "100+",        # Same as mid for coding
    }

    required = requirements.get(target_level, "51-100")

    # Calculate gap
    current_score = {"0-10": 0, "11-50": 1, "51-100": 2, "100+": 3}.get(problem_solving, 0)
    required_score = {"0-10": 0, "11-50": 1, "51-100": 2, "100+": 3}.get(required, 2)

    gap = required_score - current_score

    if gap <= 0:
        return 0

    # Time estimates (in months)
    # 0-10 → 11-50: 1 month (learn basics)
    # 11-50 → 51-100: 2 months (build intermediate skills)
    # 51-100 → 100+: 2 months (master advanced patterns)

    if gap == 1:
        return 2  # One level up
    elif gap == 2:
        return 3  # Two levels up
    elif gap == 3:
        return 4  # Three levels up (complete beginner to expert)

    return 0


def _calculate_system_design_gap_months(system_design: str, target_level: str) -> int:
    """
    Calculate months needed to close system design gap.

    System design is ONLY required for mid/senior roles.

    Realistic timelines:
    - Learning system design basics: 2-3 months (reading + designing 3-5 systems)
    - Mastering system design: 3-4 months (real-world practice + trade-offs)
    """
    if target_level == "junior":
        return 0  # Not required for junior

    # Define requirements
    requirements = {
        "mid": "once",       # Need basic exposure
        "senior": "multiple" # Need extensive experience
    }

    required = requirements.get(target_level, "once")

    # Calculate gap
    current_score = {"not-yet": 0, "learning": 0, "once": 1, "multiple": 2}.get(system_design, 0)
    required_score = {"not-yet": 0, "learning": 0, "once": 1, "multiple": 2}.get(required, 1)

    gap = required_score - current_score

    if gap <= 0:
        return 0

    # Realistic time estimates (while working full-time)
    # not-yet/learning → once: 3 months (learn fundamentals + design 3-5 systems)
    # once → multiple: 4 months (practice real-world scenarios + deepen expertise)

    if gap == 1:
        return 3
    elif gap == 2:
        return 5

    return 0


def _calculate_portfolio_gap_months(portfolio: str, target_level: str) -> int:
    """
    Calculate months needed to close portfolio gap.

    Realistic timelines:
    - Building 1 quality project: 1-2 months (while working full-time)
    - Building 2-3 projects: 3-4 months
    - Building 5+ projects: 6-9 months
    """
    # Define requirements
    requirements = {
        "junior": "limited-1-5",   # Need some projects
        "mid": "limited-1-5",      # Need solid portfolio
        "senior": "active-5+",     # Need extensive portfolio
    }

    required = requirements.get(target_level, "limited-1-5")

    # Calculate gap
    current_score = {"none": 0, "inactive": 1, "limited-1-5": 2, "active-5+": 3}.get(portfolio, 0)
    required_score = {"none": 0, "inactive": 1, "limited-1-5": 2, "active-5+": 3}.get(required, 2)

    gap = required_score - current_score

    if gap <= 0:
        return 0

    # Realistic time estimates (while working full-time)
    # inactive → limited: 3 months (revive + build 1-2 new projects)
    # none → limited: 4 months (build 2-3 projects from scratch)
    # limited → active: 5 months (build 3-4 more quality projects)
    # none → active: 8 months (build 5+ projects total)

    if gap == 1:
        return 4  # One level up (e.g., none → limited or limited → active)
    elif gap == 2:
        return 6  # Two levels up (e.g., none → active or inactive → active)
    elif gap == 3:
        return 8  # Three levels up (complete beginner → extensive portfolio)

    return 0


def _determine_target_level(target_role: str) -> str:
    """
    Determine seniority level from target role.
    """
    role_lower = target_role.lower()

    # Senior indicators
    if any(keyword in role_lower for keyword in ["senior", "lead", "staff", "principal", "architect"]):
        return "senior"

    # Mid indicators
    if any(keyword in role_lower for keyword in ["sde-2", "sde2", "mid-level", "mid level", "engineer ii"]):
        return "mid"

    # Default to mid for generic "Software Engineer" / "Backend Developer"
    if any(keyword in role_lower for keyword in ["engineer", "developer", "programmer"]) and "junior" not in role_lower:
        return "mid"

    # Junior indicators
    if any(keyword in role_lower for keyword in ["junior", "entry", "associate", "graduate", "intern", "sde-1", "sde1"]):
        return "junior"

    return "mid"  # Default to mid


def _identify_key_gap(coding_gap: int, sd_gap: int, portfolio_gap: int) -> str:
    """
    Identify the most critical gap (bottleneck).
    """
    gaps = {
        "coding": coding_gap,
        "system_design": sd_gap,
        "portfolio": portfolio_gap
    }

    # Find largest gap
    max_gap_area = max(gaps, key=gaps.get)
    max_gap_months = gaps[max_gap_area]

    if max_gap_months == 0:
        return "Interview preparation and behavioral practice"

    gap_messages = {
        "coding": "Problem-solving practice needed",
        "system_design": "System design expertise required",
        "portfolio": "Build portfolio projects"
    }

    return gap_messages.get(max_gap_area, "Skill development needed")


def _generate_milestones(
    coding_gap: int,
    sd_gap: int,
    portfolio_gap: int,
    total_months: int,
    target_role: str = "",
    quiz_responses: Dict[str, Any] = None  # NEW: Pass quiz responses to know current level
) -> List[str]:
    """
    Generate monthly milestones for the timeline.

    CRITICAL: Dependencies matter:
    - System design REQUIRES coding foundation
    - Portfolio REQUIRES coding skills
    - Can't do everything in parallel

    Args:
        target_role: Target role name (e.g., "Backend Engineer", "Full-Stack Developer")
                    Used to customize milestones based on role type
        quiz_responses: User's current skills to create personalized milestones
    """
    milestones = []

    # Get current problem-solving level (default to "0-10" if not provided)
    current_problem_solving = "0-10"
    target_company = ""
    if quiz_responses:
        current_problem_solving = quiz_responses.get("problemSolving", "0-10")
        target_company = quiz_responses.get("targetCompany", "")

    # Determine role-specific focus areas
    role_lower = target_role.lower()
    role_focus = ""
    role_projects = ""

    if "backend" in role_lower or "api" in role_lower:
        role_focus = "REST APIs and database optimization"
        role_projects = "API-based projects (e.g., REST API, microservices)"
    elif "frontend" in role_lower or "react" in role_lower or "angular" in role_lower or "vue" in role_lower:
        role_focus = "React/Vue components and responsive design"
        role_projects = "frontend projects (e.g., dashboard, SPA)"
    elif "fullstack" in role_lower or "full-stack" in role_lower or "full stack" in role_lower:
        role_focus = "full-stack development (MERN/MEAN stack)"
        role_projects = "end-to-end projects (frontend + backend + deployment)"
    elif "mobile" in role_lower or "android" in role_lower or "ios" in role_lower:
        role_focus = "mobile app development (React Native/Flutter)"
        role_projects = "mobile apps with native features"
    elif "devops" in role_lower or "sre" in role_lower or "cloud" in role_lower:
        role_focus = "CI/CD pipelines and infrastructure automation"
        role_projects = "DevOps projects (Docker, Kubernetes, CI/CD)"
    elif "data" in role_lower or "ml" in role_lower or "ai" in role_lower:
        role_focus = "data pipelines and ML model development"
        role_projects = "data/ML projects (ETL, model training, deployment)"
    else:
        role_focus = "software development fundamentals"
        role_projects = "production-quality projects"

    # Phase 1: Coding (if needed) - MUST come first
    # CRITICAL: Adapt milestone text to user's CURRENT level!
    if coding_gap > 0:
        # Determine what they're moving FROM → TO
        if current_problem_solving == "0-10":
            # Complete beginner → need fundamentals
            if coding_gap <= 2:
                milestones.append(f"Month 1-{coding_gap}: Build coding foundation (solve 50-100 problems)")
            else:
                milestones.append(f"Month 1-{coding_gap}: Master coding fundamentals (reach 100+ problems)")
        elif current_problem_solving == "11-50":
            # Some practice → need intermediate skills
            if coding_gap <= 2:
                milestones.append(f"Month 1-{coding_gap}: Strengthen problem-solving (reach 50-100 problems)")
            else:
                milestones.append(f"Month 1-{coding_gap}: Build strong foundation (reach 100+ problems)")
        elif current_problem_solving == "51-100":
            # Already at intermediate → need advanced patterns
            milestones.append(f"Month 1-{coding_gap}: Master ADVANCED patterns (solve 100+ problems)")
        else:
            # Already at 100+ → just maintenance/refinement
            milestones.append(f"Month 1-{coding_gap}: Maintain sharp problem-solving (focus on hard problems)")

    # Phase 2: Portfolio + System Design (can overlap after coding foundation)
    current_month = coding_gap + 1

    if portfolio_gap > 0 and sd_gap > 0:
        # Both needed - can partially overlap
        overlap_months = max(portfolio_gap, sd_gap)
        milestones.append(
            f"Month {current_month}-{current_month + overlap_months - 1}: "
            f"Build {2 if portfolio_gap <= 2 else 3} {role_projects} + Learn system design patterns"
        )
        current_month += overlap_months
    elif portfolio_gap > 0:
        # Only portfolio needed
        milestones.append(
            f"Month {current_month}-{current_month + portfolio_gap - 1}: "
            f"Build {2 if portfolio_gap <= 2 else '3-5'} {role_projects}"
        )
        current_month += portfolio_gap
    elif sd_gap > 0:
        # Only system design needed
        milestones.append(
            f"Month {current_month}-{current_month + sd_gap - 1}: "
            f"Master system design focused on {role_focus}"
        )
        current_month += sd_gap

    # Phase 3: Interview prep (final month) - Role-specific AND company-specific
    # Add company context to make milestones more personalized
    from label_mappings import get_company_label
    company_context = ""
    if target_company:
        company_label = get_company_label(target_company)
        if target_company in ["faang", "big-tech"]:
            company_context = f" for {company_label}"
        elif target_company in ["unicorns", "product"]:
            company_context = f" for product companies"
        elif target_company == "startups":
            company_context = f" for high-growth startups"
        elif target_company == "service":
            company_context = f" for service companies"

    if total_months > current_month:
        milestones.append(f"Month {current_month}-{total_months}: Practice {role_focus} interview questions{company_context} + mock interviews")
    elif coding_gap == 0 and sd_gap == 0 and portfolio_gap == 0:
        # Already interview-ready
        milestones.append(f"Month 1-2: Interview prep focusing on {role_focus}{company_context} + company research")

    return milestones


def calculate_timeline_to_role(
    target_role: str,
    quiz_responses: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate realistic timeline to achieve target role.

    Args:
        target_role: Target role name (e.g., "Senior Backend Engineer")
        quiz_responses: User's quiz responses with current skills

    Returns:
        {
            "min_months": 4,
            "max_months": 6,
            "timeline_text": "4-6 months",
            "confidence": "high" | "medium" | "low",
            "key_gap": "System design practice needed",
            "milestones": [
                "Month 1-2: Master coding fundamentals",
                "Month 3-4: Build 2-3 projects + Learn system design",
                "Month 5-6: Interview prep + mock interviews"
            ]
        }
    """
    # Determine target seniority level
    target_level = _determine_target_level(target_role)

    # Extract current skills
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    portfolio = quiz_responses.get("portfolio", "none")
    experience = quiz_responses.get("experience", "0-2")

    # Calculate gaps
    coding_gap_months = _calculate_coding_gap_months(problem_solving, target_level)
    sd_gap_months = _calculate_system_design_gap_months(system_design, target_level)
    portfolio_gap_months = _calculate_portfolio_gap_months(portfolio, target_level)

    # Calculate total timeline
    # CRITICAL: System design and portfolio REQUIRE coding foundation
    # Can't learn system design without coding skills

    base_months = coding_gap_months  # Must complete coding first

    # After coding, portfolio and system design can partially overlap
    if sd_gap_months > 0 and portfolio_gap_months > 0:
        # Both needed - can overlap 50% (some parallelization)
        base_months += max(sd_gap_months, portfolio_gap_months)
    else:
        # Only one needed - sequential
        base_months += sd_gap_months + portfolio_gap_months

    # Add interview prep buffer (1 month minimum)
    base_months += 1

    # Experience level affects learning speed
    experience_multiplier = {
        "0": 1.3,      # Career switchers need more time
        "0-2": 1.1,    # Slight learning curve
        "3-5": 1.0,    # Standard pace
        "5-8": 0.9,    # Faster with experience
        "8+": 0.85     # Very fast with deep experience
    }.get(experience, 1.0)

    # Target company type affects timeline (interview difficulty)
    target_company = quiz_responses.get("targetCompany", "")
    company_multiplier = {
        "faang": 1.5,           # FAANG: Rigorous process, 6-9 months
        "big-tech": 1.5,        # Big Tech: Similar to FAANG
        "unicorns": 1.3,        # Product Unicorns: Still competitive, 5-7 months
        "product": 1.2,         # Product Companies: Moderate bar, 4-6 months
        "startups": 1.0,        # Startups: Faster hiring, 3-5 months
        "service": 0.8,         # Service Companies: Lower bar, 2-4 months
    }.get(target_company, 1.0)  # Default: standard timeline

    adjusted_months = int(base_months * experience_multiplier * company_multiplier)

    # Ensure minimum 2 months, maximum 12 months
    adjusted_months = max(2, min(12, adjusted_months))

    # Calculate range (min/max)
    min_months = max(2, adjusted_months - 1)
    max_months = min(12, adjusted_months + 1)

    # Determine confidence level
    total_gaps = coding_gap_months + sd_gap_months + portfolio_gap_months
    if total_gaps == 0:
        confidence = "high"
    elif total_gaps <= 4:
        confidence = "high"
    elif total_gaps <= 6:
        confidence = "medium"
    else:
        confidence = "medium"

    # Identify key gap (bottleneck)
    key_gap = _identify_key_gap(coding_gap_months, sd_gap_months, portfolio_gap_months)

    # Generate milestones with role-specific context AND user's current level
    milestones = _generate_milestones(
        coding_gap_months,
        sd_gap_months,
        portfolio_gap_months,
        max_months,
        target_role,
        quiz_responses  # Pass quiz responses to personalize milestones
    )

    # Format timeline text
    if min_months == max_months:
        timeline_text = f"{min_months} months"
    else:
        timeline_text = f"{min_months}-{max_months} months"

    return {
        "min_months": min_months,
        "max_months": max_months,
        "timeline_text": timeline_text,
        "confidence": confidence,
        "key_gap": key_gap,
        "milestones": milestones
    }


def calculate_alternative_paths(
    quiz_responses: Dict[str, Any],
    target_role: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Calculate two alternative career paths:
    1. Faster path (easier role, shorter timeline)
    2. Alternative path (similar role, different specialization)

    Returns:
        (faster_path, alternative_path)
    """
    target_level = _determine_target_level(target_role)
    experience = quiz_responses.get("experience", "0-2")

    # Faster path: Step down one level
    if target_level == "senior":
        faster_role = "Mid-Level Software Engineer"
        faster_timeline = calculate_timeline_to_role(faster_role, quiz_responses)
        # Reduce by 2-3 months
        faster_timeline["min_months"] = max(2, faster_timeline["min_months"] - 2)
        faster_timeline["max_months"] = max(3, faster_timeline["max_months"] - 2)
        faster_timeline["timeline_text"] = f"{faster_timeline['min_months']}-{faster_timeline['max_months']} months"
        faster_timeline["role_name"] = faster_role
    elif target_level == "mid":
        faster_role = "Junior Software Engineer"
        faster_timeline = calculate_timeline_to_role(faster_role, quiz_responses)
        faster_timeline["min_months"] = max(2, faster_timeline["min_months"] - 1)
        faster_timeline["max_months"] = max(3, faster_timeline["max_months"] - 1)
        faster_timeline["timeline_text"] = f"{faster_timeline['min_months']}-{faster_timeline['max_months']} months"
        faster_timeline["role_name"] = faster_role
    else:
        # Already junior - suggest internship/entry-level
        faster_role = "Software Engineer Intern"
        faster_timeline = {
            "min_months": 2,
            "max_months": 3,
            "timeline_text": "2-3 months",
            "confidence": "high",
            "key_gap": "Build coding fundamentals",
            "milestones": [
                "Month 1-2: Complete 50 coding problems",
                "Month 3: Build 1-2 projects + Apply for internships"
            ],
            "role_name": faster_role
        }

    # Alternative path: Different specialization at same level
    # Map target role to alternative
    role_lower = target_role.lower()

    if "backend" in role_lower or "api" in role_lower:
        alt_role = f"Full-Stack Engineer" if target_level == "mid" else f"{target_level.title()} Full-Stack Engineer"
    elif "frontend" in role_lower or "react" in role_lower:
        alt_role = f"Full-Stack Engineer" if target_level == "mid" else f"{target_level.title()} Full-Stack Engineer"
    elif "fullstack" in role_lower or "full-stack" in role_lower:
        alt_role = f"Backend Engineer" if target_level == "mid" else f"{target_level.title()} Backend Engineer"
    elif "devops" in role_lower or "sre" in role_lower:
        alt_role = f"Backend Engineer" if target_level == "mid" else f"{target_level.title()} Backend Engineer"
    elif "mobile" in role_lower or "android" in role_lower or "ios" in role_lower:
        alt_role = f"Full-Stack Engineer" if target_level == "mid" else f"{target_level.title()} Full-Stack Engineer"
    else:
        # Generic fallback
        alt_role = f"Full-Stack Engineer" if target_level == "mid" else f"{target_level.title()} Full-Stack Engineer"

    # Alternative has similar timeline (maybe 1 month difference)
    alternative_timeline = calculate_timeline_to_role(target_role, quiz_responses)  # Use same target to get base
    alternative_timeline["min_months"] = max(2, alternative_timeline["min_months"] - 1)
    alternative_timeline["max_months"] = max(3, alternative_timeline["max_months"])
    alternative_timeline["timeline_text"] = f"{alternative_timeline['min_months']}-{alternative_timeline['max_months']} months"
    alternative_timeline["role_name"] = alt_role
    alternative_timeline["key_gap"] = "Learn additional tech stack"

    return faster_timeline, alternative_timeline


# Example usage for testing
if __name__ == "__main__":
    print("=" * 80)
    print("TIMELINE LOGIC TEST CASES")
    print("=" * 80)

    # Test Case 1: Junior with gaps
    test_1 = {
        "experience": "0-2",
        "problemSolving": "0-10",
        "systemDesign": "not-yet",
        "portfolio": "none"
    }
    result_1 = calculate_timeline_to_role("Junior Software Engineer", test_1)
    print(f"\nTest 1: Junior with All Gaps")
    print(f"Timeline: {result_1['timeline_text']}")
    print(f"Confidence: {result_1['confidence']}")
    print(f"Key Gap: {result_1['key_gap']}")
    print(f"Milestones: {result_1['milestones']}")

    # Test Case 2: Mid-level transition
    test_2 = {
        "experience": "3-5",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "limited-1-5"
    }
    result_2 = calculate_timeline_to_role("Senior Backend Engineer", test_2)
    faster_2, alt_2 = calculate_alternative_paths(test_2, "Senior Backend Engineer")
    print(f"\nTest 2: Mid-Level → Senior")
    print(f"Target Timeline: {result_2['timeline_text']}")
    print(f"Faster Path ({faster_2['role_name']}): {faster_2['timeline_text']}")
    print(f"Alternative Path ({alt_2['role_name']}): {alt_2['timeline_text']}")

    # Test Case 3: Already qualified
    test_3 = {
        "experience": "5-8",
        "problemSolving": "100+",
        "systemDesign": "multiple",
        "portfolio": "active-5+"
    }
    result_3 = calculate_timeline_to_role("Senior Software Engineer", test_3)
    print(f"\nTest 3: Already Qualified Senior")
    print(f"Timeline: {result_3['timeline_text']}")
    print(f"Key Gap: {result_3['key_gap']}")
    print(f"Milestones: {result_3['milestones']}")

    print("\n" + "=" * 80)
