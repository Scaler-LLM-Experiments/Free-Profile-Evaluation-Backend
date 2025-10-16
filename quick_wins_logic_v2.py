"""
IMPROVED Quick Wins logic with smart prioritization and realistic recommendations.
"""

from typing import Any, Dict, List, Tuple


def _create_quick_win(title: str, description: str, icon: str = "lightbulb", priority: int = 50) -> Dict[str, Any]:
    """
    Helper to create a QuickWin dictionary with priority.

    Priority scale:
    - 90-100: Critical, highest impact
    - 70-89: High impact
    - 50-69: Medium impact
    - 30-49: Low impact
    - 0-29: Nice to have
    """
    return {
        "title": title,
        "description": description,
        "icon": icon,
        "_priority": priority  # Internal field for sorting
    }


def _determine_user_level(quiz_responses: Dict[str, Any]) -> str:
    """Determine user's overall skill level: beginner, intermediate, or advanced."""
    experience = quiz_responses.get("experience", "0")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")

    # Advanced: 5+ years OR (3-5 years + 100+ problems + system design experience)
    if experience in ["5+", "5-8", "8+"]:
        return "advanced"
    if experience == "3-5" and problem_solving == "100+" and system_design in ["once", "multiple"]:
        return "advanced"

    # Beginner: 0-2 years OR low problem solving
    if experience in ["0", "0-2"]:
        return "beginner"
    if problem_solving in ["0-10", "11-50"]:
        return "beginner"

    # Everything else is intermediate
    return "intermediate"


def generate_quick_wins(background: str, quiz_responses: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate 3-5 specific, realistic quick wins with smart prioritization.
    """

    quick_wins = []
    user_level = _determine_user_level(quiz_responses)

    current_role = quiz_responses.get("currentRole", "")
    experience = quiz_responses.get("experience", "")
    target_role = quiz_responses.get("targetRole", "")
    system_design = quiz_responses.get("systemDesign", "")
    portfolio = quiz_responses.get("portfolio", "")
    problem_solving = quiz_responses.get("problemSolving", "")

    if background == "non-tech":
        # NON-TECH BACKGROUND - Start with basics, build gradually

        # HIGHEST PRIORITY: Get started with coding
        if current_role == "non-tech":
            quick_wins.append(_create_quick_win(
                "Start with Programming Basics",
                "Try 'Intro to Python' on Scaler Topics or W3Schools. Build a small automation like Excel-to-CSV script.",
                "code",
                priority=95
            ))
        elif current_role == "it-services":
            quick_wins.append(_create_quick_win(
                "Brush Up Coding Fundamentals",
                "Focus on loops and conditions. Solve 5 beginner problems on HackerRank.",
                "code",
                priority=90
            ))
        elif current_role == "technical":
            quick_wins.append(_create_quick_win(
                "Build a CRUD App",
                "Revisit core CS concepts and build a basic CRUD application using Python or Node.js.",
                "rocket",
                priority=85
            ))

        # HIGH PRIORITY: First project based on experience
        if experience in ["0", "0-2"]:
            quick_wins.append(_create_quick_win(
                "Build Your First Project",
                "Create a mini-project like a to-do app or calculator to showcase basic skills.",
                "rocket",
                priority=85
            ))
        elif experience == "3-5":
            quick_wins.append(_create_quick_win(
                "Showcase Transition Intent",
                "Add 2-3 measurable projects to your portfolio showing your transition to tech.",
                "trophy",
                priority=80
            ))

        # MEDIUM PRIORITY: Target role specific (only if they have some basics)
        if problem_solving in ["11-50", "51-100", "100+"]:  # Only if they've started practicing
            if target_role in ["backend", "backend-dev", "backend-sde"]:
                quick_wins.append(_create_quick_win(
                    "Build a Simple REST API",
                    "Create a basic REST API using Flask or Django with 2-3 endpoints. Learn SQL basics.",
                    "code",
                    priority=75
                ))
            elif target_role in ["fullstack", "fullstack-dev", "fullstack-sde"]:
                quick_wins.append(_create_quick_win(
                    "Build a Web App",
                    "Create a simple web app with HTML, CSS, JavaScript. Host it on GitHub Pages or Netlify.",
                    "rocket",
                    priority=75
                ))

        # LOW PRIORITY: Setup GitHub (only if they don't have one)
        if portfolio in ["none", "no-portfolio"]:
            quick_wins.append(_create_quick_win(
                "Set Up GitHub Profile",
                "Create GitHub account and upload 1-2 practice projects to start building your portfolio.",
                "target",
                priority=70
            ))

    else:
        # TECH BACKGROUND - Focus on interview prep and skill deepening

        # HIGHEST PRIORITY: Problem solving based on current level
        if problem_solving == "0-10":
            quick_wins.append(_create_quick_win(
                "Build Coding Foundation",
                "Solve 20 easy problems on LeetCode/HackerRank focusing on arrays and strings.",
                "code",
                priority=100
            ))
        elif problem_solving == "11-50":
            quick_wins.append(_create_quick_win(
                "Strengthen Problem Solving",
                "Solve 30 medium problems focusing on Trees, Graphs, and Dynamic Programming.",
                "trophy",
                priority=95
            ))
        elif problem_solving == "51-100":
            quick_wins.append(_create_quick_win(
                "Master Advanced Patterns",
                "Solve 20 hard problems and participate in 2 weekly coding contests.",
                "trophy",
                priority=90
            ))

        # HIGH PRIORITY: System Design appropriate to level
        if system_design == "not-yet" and user_level in ["intermediate", "advanced"]:
            quick_wins.append(_create_quick_win(
                "Start System Design Prep",
                "Read 'Designing Data-Intensive Applications' and design 1 system (URL shortener, Chat app).",
                "books",
                priority=95
            ))
        elif system_design == "once" and user_level == "advanced":
            quick_wins.append(_create_quick_win(
                "Deep Dive System Design",
                "Study 5 real-world system designs (Netflix, Uber, Instagram). Focus on trade-offs and scalability.",
                "books",
                priority=90
            ))
        elif system_design == "multiple":
            quick_wins.append(_create_quick_win(
                "Master Low-Level Design",
                "Practice object-oriented design patterns. Solve 10 LLD problems (Parking Lot, Library System).",
                "lightbulb",
                priority=85
            ))

        # MEDIUM-HIGH PRIORITY: Role-specific preparation
        if target_role in ["faang-sde", "faang"]:
            if experience in ["3-5", "5+", "5-8", "8+"]:
                quick_wins.append(_create_quick_win(
                    "FAANG Interview Prep",
                    "Complete 90-day prep: 60 problems + 20 system design + 10 behavioral questions.",
                    "trophy",
                    priority=95
                ))
        elif target_role == "tech-lead" and experience in ["5+", "5-8", "8+"]:
            quick_wins.append(_create_quick_win(
                "Leadership Preparation",
                "Write 3 design docs for past projects. Practice team collaboration and mentoring.",
                "certificate",
                priority=85
            ))

        # MEDIUM PRIORITY: Portfolio improvements
        if portfolio == "none" and user_level != "beginner":
            quick_wins.append(_create_quick_win(
                "Build GitHub Presence",
                "Create GitHub account and upload 3-5 well-documented projects from your work.",
                "rocket",
                priority=75
            ))
        elif portfolio in ["limited-1-5", "limited-1to5"]:
            quick_wins.append(_create_quick_win(
                "Expand Portfolio Quality",
                "Add README, tests, and CI/CD to existing projects. Host 1 project live.",
                "rocket",
                priority=70
            ))
        elif portfolio == "active-5+":
            quick_wins.append(_create_quick_win(
                "Polish Existing Projects",
                "Add comprehensive documentation, demo videos, and deploy to production.",
                "certificate",
                priority=60
            ))

        # MEDIUM PRIORITY: Experience-based knowledge sharing
        if experience in ["3-5", "5+", "5-8", "8+"] and user_level in ["intermediate", "advanced"]:
            quick_wins.append(_create_quick_win(
                "Build Technical Brand",
                "Write 3 technical blog posts or create tutorial videos on topics you've mastered.",
                "certificate",
                priority=65
            ))

    # Sort by priority (highest first) and remove priority field
    quick_wins.sort(key=lambda x: x["_priority"], reverse=True)

    # Remove internal _priority field and return top 5
    clean_wins = []
    for win in quick_wins[:5]:
        clean_wins.append({
            "title": win["title"],
            "description": win["description"],
            "icon": win["icon"]
        })

    return clean_wins
