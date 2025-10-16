"""
Hardcoded Quick Wins logic based on user profile.
This bypasses GPT to ensure consistent, specific recommendations.
"""

from typing import Any, Dict, List


def _create_quick_win(title: str, description: str, icon: str = "lightbulb") -> Dict[str, str]:
    """Helper to create a QuickWin dictionary."""
    return {
        "title": title,
        "description": description,
        "icon": icon
    }


def generate_quick_wins(background: str, quiz_responses: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate 3-5 specific quick wins based on user's profile.

    Priority order:
    1. Current role specific recommendations
    2. Experience level recommendations
    3. Target role recommendations
    4. Skills-based recommendations (code comfort, system design, portfolio)
    5. Motivation-based recommendations
    """

    quick_wins = []

    current_role = quiz_responses.get("currentRole", "")
    experience = quiz_responses.get("experience", "")
    target_role = quiz_responses.get("targetRole", "")
    system_design = quiz_responses.get("systemDesign", "")
    portfolio = quiz_responses.get("portfolio", "")
    problem_solving = quiz_responses.get("problemSolving", "")

    if background == "non-tech":
        # Non-Tech Background Quick Wins

        # Current Role based
        if current_role == "non-tech":
            quick_wins.append(_create_quick_win(
                "Start with Programming Basics",
                "Try 'Intro to Python' on Scaler Topics or W3Schools. Build a small automation like Excel-to-CSV script.",
                "code"
            ))
        elif current_role == "it-services":
            quick_wins.append(_create_quick_win(
                "Brush Up Coding Fundamentals",
                "Focus on loops and conditions. Solve 5 beginner problems on HackerRank.",
                "code"
            ))
        elif current_role == "technical":
            quick_wins.append(_create_quick_win(
                "Build a CRUD App",
                "Revisit core CS concepts and build a basic CRUD application using Python or Node.js.",
                "rocket"
            ))
        elif current_role == "fresh-graduate":
            quick_wins.append(_create_quick_win(
                "Learn DSA Basics",
                "Learn DSA basics and attempt 10 beginner-level problems this week.",
                "books"
            ))

        # Experience based
        if experience == "0":
            quick_wins.append(_create_quick_win(
                "Set Up Your Dev Environment",
                "Create a GitHub account and complete 1 online programming basics course.",
                "target"
            ))
        elif experience == "0-2":
            quick_wins.append(_create_quick_win(
                "Build Your First Project",
                "Create a mini-project like a to-do app or data dashboard to showcase skills.",
                "rocket"
            ))
        elif experience == "3-5":
            quick_wins.append(_create_quick_win(
                "Showcase Transition Intent",
                "Add measurable projects to your portfolio showing your transition to tech.",
                "trophy"
            ))
        elif experience in ["5+", "5-8", "8+"]:
            quick_wins.append(_create_quick_win(
                "Update Your Personal Brand",
                "Update resume headline to reflect transition goals (e.g., 'Operations Manager → Aspiring Backend Engineer').",
                "certificate"
            ))

        # Target Role based
        if target_role in ["backend", "backend-dev", "backend-sde"]:
            quick_wins.append(_create_quick_win(
                "Build a REST API",
                "Create a small REST API using Flask or Django. Learn SQL basics alongside.",
                "code"
            ))
        elif target_role in ["fullstack", "fullstack-dev", "fullstack-sde"]:
            quick_wins.append(_create_quick_win(
                "Build a Web App",
                "Create a simple web app with HTML, CSS, JavaScript and host it on GitHub Pages.",
                "rocket"
            ))
        elif target_role in ["data-ml", "data-engineer", "ml-engineer"]:
            quick_wins.append(_create_quick_win(
                "Build an ML Project",
                "Complete 1 mini project using Pandas & scikit-learn (e.g., movie recommender).",
                "lightbulb"
            ))
        elif target_role in ["data-analyst"]:
            quick_wins.append(_create_quick_win(
                "Master Data Tools",
                "Learn Excel → SQL → Power BI sequence. Analyze a public dataset.",
                "chart-bar"
            ))

    else:
        # Tech Background Quick Wins

        # Current Role based
        if current_role in ["student-freshgrad", "student"]:
            quick_wins.append(_create_quick_win(
                "Build Coding Momentum",
                "Complete 10 DSA problems this week. Attend 1 coding contest.",
                "trophy"
            ))
        elif current_role == "swe-product":
            quick_wins.append(_create_quick_win(
                "Daily Concept Revision",
                "Revise 1 core concept daily focusing on System Design or DSA.",
                "books"
            ))
        elif current_role == "swe-service":
            quick_wins.append(_create_quick_win(
                "Expand Tech Stack",
                "Build a side project or explore a new tech stack (MERN, backend frameworks).",
                "rocket"
            ))
        elif current_role == "career-switcher":
            quick_wins.append(_create_quick_win(
                "Document Your Journey",
                "Start documenting your learnings on GitHub and LinkedIn to build visibility.",
                "certificate"
            ))

        # Experience based
        if experience == "0":
            quick_wins.append(_create_quick_win(
                "Master Fundamentals",
                "Focus on programming fundamentals: arrays, loops, functions.",
                "code"
            ))
        elif experience == "0-2":
            quick_wins.append(_create_quick_win(
                "Build Resume Project",
                "Create a resume-ready project showing practical application of skills.",
                "rocket"
            ))
        elif experience == "3-5":
            quick_wins.append(_create_quick_win(
                "Share Your Knowledge",
                "Mentor juniors or write technical blog posts to establish expertise.",
                "certificate"
            ))
        elif experience in ["5+", "5-8", "8+"]:
            quick_wins.append(_create_quick_win(
                "Prepare for Leadership",
                "Learn system design patterns and develop mentoring skills.",
                "trophy"
            ))

        # Target Role based
        if target_role in ["faang-sde", "faang"]:
            quick_wins.append(_create_quick_win(
                "Start 90-Day Code Streak",
                "Begin a 90-day coding streak. Revise system design concepts weekly.",
                "trophy"
            ))
        elif target_role in ["backend", "backend-sde"]:
            quick_wins.append(_create_quick_win(
                "Build Production API",
                "Build a production-ready API with Node/Express or Django.",
                "code"
            ))
        elif target_role in ["data-ml", "data-engineer", "ml-engineer"]:
            quick_wins.append(_create_quick_win(
                "Join Kaggle Competitions",
                "Participate in Kaggle competitions or build 1 ML model with scikit-learn.",
                "lightbulb"
            ))
        elif target_role in ["fullstack", "fullstack-sde"]:
            quick_wins.append(_create_quick_win(
                "Build Full Stack App",
                "Create a complete CRUD app using MERN stack or Django + React.",
                "rocket"
            ))
        elif target_role == "tech-lead":
            quick_wins.append(_create_quick_win(
                "Practice System Design",
                "Write design docs for a personal project. Focus on scalability concepts.",
                "books"
            ))

        # System Design based
        if system_design == "multiple":
            quick_wins.append(_create_quick_win(
                "Advanced Design Patterns",
                "Try low-level design problems (class diagrams, API design patterns).",
                "lightbulb"
            ))
        elif system_design == "once":
            quick_wins.append(_create_quick_win(
                "Study Design Case Studies",
                "Read 2 new system design case studies (TinyURL, Instagram, etc.).",
                "books"
            ))
        elif system_design == "not-yet":
            quick_wins.append(_create_quick_win(
                "Start with System Design",
                "Watch 1 short 'System Design for Beginners' video today.",
                "target"
            ))

        # Portfolio based
        if portfolio == "active-5+":
            quick_wins.append(_create_quick_win(
                "Polish Your Projects",
                "Add comprehensive README files and host one project live.",
                "rocket"
            ))
        elif portfolio in ["limited-1-5", "limited-1to5"]:
            quick_wins.append(_create_quick_win(
                "Expand Your Portfolio",
                "Commit 1 new project this week to expand your GitHub presence.",
                "code"
            ))
        elif portfolio == "inactive":
            quick_wins.append(_create_quick_win(
                "Revive Your GitHub",
                "Upload your practice code or course projects to GitHub.",
                "target"
            ))
        elif portfolio in ["none", "no-portfolio"]:
            quick_wins.append(_create_quick_win(
                "Create GitHub Account",
                "Create a GitHub account and push your first project today.",
                "certificate"
            ))

    # Return top 5 unique quick wins
    # Remove duplicates while preserving order
    seen_titles = set()
    unique_wins = []
    for win in quick_wins:
        if win["title"] not in seen_titles:
            seen_titles.add(win["title"])
            unique_wins.append(win)

    return unique_wins[:5]
