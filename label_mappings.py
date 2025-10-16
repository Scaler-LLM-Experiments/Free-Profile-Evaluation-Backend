"""
Human-readable label mappings from frontend quiz values.

Maps technical IDs (e.g., 'swe-product', 'senior-backend') to display labels.
Source: frontend/src/components/quiz/ChattyQuizScreens.js
"""

# Current Role Labels (Question 1 - Tech)
CURRENT_ROLE_LABELS = {
    'swe-product': 'Software Engineer - Product Company',
    'swe-service': 'Software Engineer - Service Company',
    'devops': 'DevOps / Cloud / Infrastructure Engineer',
    'qa-support': 'QA / Support / Other Technical Role',

    # Non-Tech backgrounds
    'sales-marketing': 'Sales / Marketing / Business',
    'operations': 'Operations / Consulting / PM',
    'design': 'Design (UI/UX / Graphic / Product)',
    'finance': 'Finance / Accounting / Banking',
    'other': 'Other Non-Tech / Fresh Grad',
    'career-switcher': 'Career Switcher'
}

# Target Role Labels (Question 5 - Tech, Question 1 - Non-Tech)
TARGET_ROLE_LABELS = {
    # Tech roles
    'senior-backend': 'Senior Backend Engineer',
    'senior-fullstack': 'Senior Full-Stack Engineer',
    'backend-sde': 'Backend Engineer',
    'fullstack-sde': 'Full-Stack Engineer',
    'data-ml': 'Data / ML Engineer',
    'tech-lead': 'Tech Lead / Staff Engineer',

    # Non-tech target roles
    'backend': 'Backend Engineer',
    'fullstack': 'Full-Stack Engineer',
    'data-ml': 'Data / ML Engineer',
    'frontend': 'Frontend Engineer',
    'not-sure': 'Exploring Tech Roles',
    'exploring': 'Exploring Tech Roles'
}

# Target Company Labels (Question 6 - Tech, Question 3 - Non-Tech)
TARGET_COMPANY_LABELS = {
    # Tech path
    'faang': 'FAANG / Big Tech',
    'unicorns': 'Product Unicorns / Scaleups',
    'startups': 'High Growth Startups',
    'better-service': 'Service Companies',
    'evaluating': 'All Company Types',

    # Non-tech path
    'any-tech': 'Any Tech Company',
    'product': 'Product Companies',
    'service': 'Service Companies',
    'faang-longterm': 'FAANG / Big Tech (Long-term)',
    'not-sure': 'All Company Types',

    # Generic fallback
    'Not specified': 'Tech Companies',
    'Transitioning from non-tech background': 'Entry-level Tech Companies'
}

# Problem Solving Labels (Question 7 - Tech)
PROBLEM_SOLVING_LABELS = {
    '100+': 'Very Active (100+ problems)',
    '51-100': 'Moderately Active (50-100 problems)',
    '11-50': 'Somewhat Active (10-50 problems)',
    '0-10': 'Not Active (0-10 problems)'
}

# System Design Labels (Question 8 - Tech)
SYSTEM_DESIGN_LABELS = {
    'multiple': 'Led design discussions',
    'once': 'Participated in discussions',
    'learning': 'Self-learning only',
    'not-yet': 'Not yet, will learn'
}

# Portfolio Labels (Question 9 - Tech)
PORTFOLIO_LABELS = {
    'active-5+': 'Active (5+ public repos)',
    'limited-1-5': 'Limited (1-5 repos)',
    'inactive': 'Inactive (old activity)',
    'none': 'No portfolio yet'
}

# Experience Labels
EXPERIENCE_LABELS = {
    '0': '0 years (Fresh grad)',
    '0-2': '0-2 years',
    '3-5': '3-5 years',
    '5-8': '5-8 years',
    '8+': '8+ years',
    '5+': '5+ years'
}

# Primary Goal Labels (Question 4 - Tech)
PRIMARY_GOAL_LABELS = {
    'better-company': 'Move to a better company (same level)',
    'level-up': 'Level up (senior role / promotion)',
    'higher-comp': 'Higher compensation',
    'switch-domain': 'Switch to different tech domain',
    'upskilling': 'Upskilling in current role'
}


def get_role_label(role_value: str) -> str:
    """Get human-readable label for target role."""
    return TARGET_ROLE_LABELS.get(role_value, role_value.title())


def get_company_label(company_value: str) -> str:
    """Get human-readable label for target company."""
    return TARGET_COMPANY_LABELS.get(company_value, 'Tech Companies')


def get_current_role_label(role_value: str) -> str:
    """Get human-readable label for current role."""
    return CURRENT_ROLE_LABELS.get(role_value, role_value.title())


def format_job_title(target_role: str, target_company: str) -> str:
    """
    Format job title by concatenating role + company labels.

    Examples:
        - 'senior-backend' + 'faang' → 'Senior Backend Engineer - FAANG / Big Tech'
        - 'fullstack-sde' + 'unicorns' → 'Full-Stack Engineer - Product Unicorns / Scaleups'
    """
    role_label = get_role_label(target_role)
    company_label = get_company_label(target_company)
    return f"{role_label} - {company_label}"


def get_experience_label(exp_value: str) -> str:
    """Get human-readable label for experience."""
    return EXPERIENCE_LABELS.get(exp_value, exp_value)


def get_problem_solving_label(ps_value: str) -> str:
    """Get human-readable label for problem solving activity."""
    return PROBLEM_SOLVING_LABELS.get(ps_value, ps_value)


def get_system_design_label(sd_value: str) -> str:
    """Get human-readable label for system design comfort."""
    return SYSTEM_DESIGN_LABELS.get(sd_value, sd_value)


def get_portfolio_label(port_value: str) -> str:
    """Get human-readable label for portfolio status."""
    return PORTFOLIO_LABELS.get(port_value, port_value)


def get_primary_goal_label(goal_value: str) -> str:
    """Get human-readable label for primary goal."""
    return PRIMARY_GOAL_LABELS.get(goal_value, goal_value)
