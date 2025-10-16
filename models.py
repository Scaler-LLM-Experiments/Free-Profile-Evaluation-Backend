from enum import Enum
from typing import List, TYPE_CHECKING

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from models_raw import FullProfileEvaluationResponseRaw


# Enum for profile strength status
class ProfileStrengthStatus(Enum):
    NEEDS_IMPROVEMENT = "Needs Improvement"
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"


# Enum for interview readiness status
class InterviewReadinessStatus(Enum):
    NEEDS_IMPROVEMENT = "Needs Improvement"
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"


# Enum for success likelihood
class SuccessLikelihoodStatus(Enum):
    NEEDS_IMPROVEMENT = "Needs significant improvement"
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"


# Enum for experience levels
class ExperienceLevel(Enum):
    ENTRY = "Entry"
    SENIOR = "Senior"
    MID_SENIOR = "Mid-Senior"
    EXPERT = "Expert"


class PeerComparisonLabel(Enum):
    BELOW_AVERAGE = "Below Average"
    AVERAGE = "Average"
    ABOVE_AVERAGE = "Above Average"
    TOP_PERFORMER = "Top Performer"


class RecommendedRole(BaseModel):
    title: str
    seniority: ExperienceLevel
    reason: str
    # Timeline fields for career transition
    timeline_text: str = Field(
        default="4-6 months",
        description="Human-readable timeline (e.g., '4-6 months', '2-3 months')"
    )
    min_months: int = Field(
        default=4,
        ge=1,
        le=24,
        description="Minimum months to achieve this role"
    )
    max_months: int = Field(
        default=6,
        ge=1,
        le=24,
        description="Maximum months to achieve this role"
    )
    key_gap: str = Field(
        default="Skill development needed",
        description="Primary bottleneck or gap to address"
    )
    milestones: List[str] = Field(
        default_factory=list,
        description="Monthly milestones for achieving this role"
    )
    confidence: str = Field(
        default="medium",
        description="Confidence level: 'high', 'medium', or 'low'"
    )


class CurrentProfileKeyStat(BaseModel):
    label: str = Field(..., description="Stat label (e.g., 'Experience', 'Current Role')")
    value: str = Field(..., description="Stat value (e.g., '3-5 years', 'Software Engineer')")
    icon: str = Field(default="circle", description="Phosphor icon name")


class CurrentProfileSummary(BaseModel):
    title: str = Field(default="Your Current Profile", description="Section title")
    summary: str = Field(..., description="Conversational summary of current profile")
    key_stats: List[CurrentProfileKeyStat] = Field(
        default_factory=list,
        description="Key statistics about current profile"
    )


class QuickWin(BaseModel):
    title: str = Field(
        ..., description="Short, catchy title for the quick win (4-6 words max)"
    )
    description: str = Field(
        ..., description="Detailed description explaining how to achieve this quick win"
    )
    icon: str = Field(
        default="lightbulb",
        description="Icon name from Phosphor icons (lightbulb, trophy, target, rocket, code, books, certificate, etc.)"
    )


class SkillAnalysis(BaseModel):
    strengths: List[str] = Field(
        ..., min_length=3, description="List of identified strengths"
    )
    areas_to_develop: List[str] = Field(
        ..., min_length=3, description="List of areas to develop"
    )


class ExperienceBenchmark(BaseModel):
    your_experience_years: str
    typical_for_target_role_years: str = Field(
        ...,
        description="Typical experience years for the target role",
        examples=["3-5", "5-7", "7-10", "0-1", "1-3", "10+"],
    )
    gap_analysis: str


class InterviewReadiness(BaseModel):
    technical_interview_percent: int = Field(
        ..., ge=0, le=100, description="Readiness percentage for technical interviews"
    )
    hr_behavioral_percent: int = Field(
        ...,
        ge=0,
        le=100,
        description="Readiness percentage for HR behavioral interviews",
    )
    technical_notes: str


class PeerComparisonMetrics(BaseModel):
    profile_strength_percent: int = Field(
        ..., ge=0, le=100, description="Profile strength percentage"
    )
    better_than_peers_percent: int = Field(
        ..., ge=0, le=100, description="Percentage better than peers"
    )


class PeerComparison(BaseModel):
    percentile: int
    potential_percentile: int = Field(
        default=75,
        ge=0,
        le=100,
        description="Potential percentile if gaps are addressed (shown as lighter shade)"
    )
    peer_group_description: str = Field(
        default="Similar professionals in tech",
        description="Description of peer group being compared against (e.g., 'Senior Software Engineers at Big Tech firms')"
    )
    label: PeerComparisonLabel = Field(..., description="Peer comparison label")
    summary: str
    metrics: PeerComparisonMetrics


class SuccessLikelihood(BaseModel):
    score_percent: int
    label: str
    status: SuccessLikelihoodStatus
    notes: str


class ProfileEvaluation(BaseModel):
    profile_strength_score: int = Field(
        ..., ge=0, le=100, description="Overall profile score from 0 to 100"
    )
    profile_strength_status: ProfileStrengthStatus = Field(
        ..., description="Status of profile strength"
    )
    profile_strength_notes: str

    # Current profile summary (for Career Transition section)
    current_profile: CurrentProfileSummary = Field(
        ..., description="Detailed summary of user's current profile based on quiz responses"
    )

    skill_analysis: SkillAnalysis
    recommended_tools: List[str] = Field(
        ...,
        min_length=3,
        description="List of recommended tools",
        examples=[
            "Data Science Libraries (e.g., Pandas, NumPy)",
            "Web Development Frameworks (e.g., React, Django)",
            "Design System Resources (e.g., Figma, Sketch)",
            "Cloud Platforms (e.g., AWS, Azure, GCP)",
            "Machine Learning Frameworks (e.g., TensorFlow, PyTorch, Scikit-learn)",
            "Version Control Systems (e.g., Git, GitHub, GitLab, Bitbucket)",
            "Containerization & Orchestration (e.g., Docker, Kubernetes, Helm)",
            "Project Management Tools (e.g., Jira, Trello, Asana, ClickUp)",
            "Collaboration Platforms (e.g., Slack, Microsoft Teams, Discord)",
            "Database Systems (e.g., PostgreSQL, MongoDB, Redis, MySQL)",
            "Testing Frameworks (e.g., Pytest, Jest, Cypress, Mocha)",
            "CI/CD Pipelines (e.g., GitHub Actions, Jenkins, GitLab CI)",
            "Data Visualization Tools (e.g., Tableau, Power BI, Matplotlib, D3.js)",
            "API Development & Testing (e.g., Postman, Swagger, Insomnia)",
            "Security & Authentication (e.g., OAuth, JWT, Keycloak, Auth0)",
        ],
    )

    experience_benchmark: ExperienceBenchmark
    interview_readiness: InterviewReadiness
    peer_comparison: PeerComparison
    success_likelihood: SuccessLikelihood

    quick_wins: List[QuickWin] = Field(
        ...,
        min_length=3,
        description="List of quick wins to improve profile with title and description"
    )
    opportunities_you_qualify_for: List[str] = Field(
        ...,
        description="List of job opportunities you currently qualify for",
        min_length=0
    )
    recommended_roles_based_on_interests: List[RecommendedRole]

    badges: List[str]



# Full response model
class FullProfileEvaluationResponse(BaseModel):
    profile_evaluation: ProfileEvaluation


# --- Helpers to hydrate derived fields -----------------------------------------------------

_PROFILE_STATUS_THRESHOLDS = (
    (85, ProfileStrengthStatus.EXCELLENT),
    (70, ProfileStrengthStatus.GOOD),
    (50, ProfileStrengthStatus.AVERAGE),
)

_SUCCESS_STATUS_THRESHOLDS = (
    (85, SuccessLikelihoodStatus.EXCELLENT),
    (70, SuccessLikelihoodStatus.GOOD),
    (50, SuccessLikelihoodStatus.AVERAGE),
)

_PEER_COMPARISON_THRESHOLDS = (
    (90, PeerComparisonLabel.TOP_PERFORMER),
    (70, PeerComparisonLabel.ABOVE_AVERAGE),
    (40, PeerComparisonLabel.AVERAGE),
)

_SUCCESS_LABEL_BY_STATUS = {
    SuccessLikelihoodStatus.EXCELLENT: "High likelihood of success",
    SuccessLikelihoodStatus.GOOD: "Strong likelihood of success",
    SuccessLikelihoodStatus.AVERAGE: "Moderate likelihood of success",
    SuccessLikelihoodStatus.NEEDS_IMPROVEMENT: "Low likelihood of success",
}


def _clamp_percent(value: int) -> int:
    return max(0, min(100, value))


def _lookup_by_threshold(value: int, thresholds, default):
    for cutoff, result in thresholds:
        if value >= cutoff:
            return result
    return default


def _profile_strength_status_from_score(score: int) -> ProfileStrengthStatus:
    return _lookup_by_threshold(
        _clamp_percent(score),
        _PROFILE_STATUS_THRESHOLDS,
        ProfileStrengthStatus.NEEDS_IMPROVEMENT,
    )


def _success_status_from_score(score: int) -> SuccessLikelihoodStatus:
    return _lookup_by_threshold(
        _clamp_percent(score),
        _SUCCESS_STATUS_THRESHOLDS,
        SuccessLikelihoodStatus.NEEDS_IMPROVEMENT,
    )


def _success_label_from_status(status: SuccessLikelihoodStatus) -> str:
    return _SUCCESS_LABEL_BY_STATUS[status]


def _peer_comparison_label_from_percentile(percentile: int) -> PeerComparisonLabel:
    return _lookup_by_threshold(
        _clamp_percent(percentile),
        _PEER_COMPARISON_THRESHOLDS,
        PeerComparisonLabel.BELOW_AVERAGE,
    )


def enrich_full_profile_evaluation(
    raw: "FullProfileEvaluationResponseRaw",
) -> FullProfileEvaluationResponse:
    """Augment a raw response with derived fields and validate against the full schema."""

    data = raw.model_dump()
    profile = data["profile_evaluation"]
    profile["profile_strength_status"] = _profile_strength_status_from_score(
        profile["profile_strength_score"]
    )

    # Apply motivational floor to peer comparison (minimum 35%)
    # This prevents demotivation - same philosophy as profile_strength_score 45% floor
    peer = profile["peer_comparison"]
    peer["percentile"] = max(35, peer["percentile"])
    peer["label"] = _peer_comparison_label_from_percentile(peer["percentile"])

    # Apply motivational floor to success likelihood (minimum 35%)
    success = profile["success_likelihood"]
    success["score_percent"] = max(35, success["score_percent"])
    success_status = _success_status_from_score(success["score_percent"])
    success["status"] = success_status
    success["label"] = _success_label_from_status(success_status)

    return FullProfileEvaluationResponse.model_validate(data)


# Example usage
profile_evaluation_data = {
    "profile_strength_score": 40,
    "profile_strength_status": "Needs Improvement",
    "profile_strength_notes": "This is calculated from your experience, learning progress, coding comfort, and time commitment. Improving any of these will raise your score.",
    "skill_analysis": {
        "strengths": ["Technology Interest", "Technology Interest"],
        "areas_to_develop": [
            "Programming Language Proficiency",
            "Technical Interview Skills",
            "Industry Knowledge",
            "Basic Coding Skills",
        ],
    },
    "recommended_tools": [
        "VS Code",
        "Git",
        "GitHub",
        "FreeCodeCamp",
        "Codecademy",
        "MDN Web Docs",
        "React Native",
        "Flutter",
    ],
    "experience_benchmark": {
        "your_experience_years": "0-2",
        "typical_for_target_role_years": "0-2",
        "gap_analysis": "On Track",
    },
    "interview_readiness": {
        "technical_interview_percent": 50,
        "hr_behavioral_percent": 65,
        "technical_notes": "Technical is influenced by coding practice and system design exposure; HR is influenced by experience and communication. Increase practice frequency to improve.",
    },
    "peer_comparison": {
        "percentile": 40,
        "label": "Below Average",
        "summary": "You rank better than 40% of similar profiles based on your profile strength relative to others targeting similar roles.",
        "metrics": {"profile_strength_percent": 40, "better_than_peers_percent": 40},
    },
    "success_likelihood": {
        "score_percent": 40,
        "label": "Likelihood of Success",
        "status": "Needs significant improvement",
        "notes": "Derived from overall profile strength and time commitment. Increase weekly practice or time to boost this.",
    },
    "quick_wins": [
        {
            "title": "Start with Coding Tutorials",
            "description": "Begin with basic coding tutorials to build foundational skills",
            "icon": "code"
        },
        {
            "title": "Build Portfolio Project",
            "description": "Create a simple portfolio project to showcase your skills",
            "icon": "rocket"
        },
    ],
    "opportunities_you_qualify_for": [],
    "recommended_roles_based_on_interests": [
        {
            "title": "iOS Developer",
            "seniority": "Entry",
            "reason": "Interest in Mobile Development → iOS Developer because your interest in mobile technologies and Apple ecosystem aligns with this specialized role in iOS app development.",
        },
        {
            "title": "Android Developer",
            "seniority": "Entry",
            "reason": "Interest in Mobile Development → Android Developer because your interest in mobile technologies and Android platform makes you perfect for this role in Android app development.",
        },
        {
            "title": "React Native Developer",
            "seniority": "Mid-Senior",
            "reason": "Interest in Mobile Development → React Native Developer because your interest in mobile development combined with web technologies makes you ideal for cross-platform mobile development.",
        },
        {
            "title": "Flutter Developer",
            "seniority": "Mid-Senior",
            "reason": "Interest in Mobile Development → Flutter Developer because your interest in development and cross-platform solutions aligns with this role using Google's Flutter framework.",
        },
        {
            "title": "Health Tech Developer",
            "seniority": "Mid-Senior",
            "reason": "Interest in Health Tech → Health Tech Developer because your interest in healthcare technology and programming skills make you well-suited for this role that develops health-related software.",
        },
    ],
    "badges": ["Needs Coding Practice"],
    "source_images": [
        "/mnt/data/c3044c97-f9ea-45f7-ab9c-09ad4987b88e.png",
        "/mnt/data/f030b724-8200-483d-8cd9-3f84ce73bda1.png",
    ],
}
