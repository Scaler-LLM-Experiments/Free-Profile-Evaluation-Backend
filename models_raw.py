"""Raw response models without derived status/label fields."""
from typing import List

from pydantic import BaseModel, Field

from models import ExperienceLevel


class RecommendedRoleRaw(BaseModel):
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


class CurrentProfileKeyStatRaw(BaseModel):
    label: str = Field(..., description="Stat label (e.g., 'Experience', 'Current Role')")
    value: str = Field(..., description="Stat value (e.g., '3-5 years', 'Software Engineer')")
    icon: str = Field(default="circle", description="Phosphor icon name")


class CurrentProfileSummaryRaw(BaseModel):
    title: str = Field(default="Your Current Profile", description="Section title")
    summary: str = Field(..., description="Conversational summary of current profile")
    key_stats: List[CurrentProfileKeyStatRaw] = Field(
        default_factory=list,
        description="Key statistics about current profile"
    )


class SkillAnalysisRaw(BaseModel):
    strengths: List[str] = Field(
        ..., min_length=3, description="List of identified strengths"
    )
    areas_to_develop: List[str] = Field(
        ..., min_length=3, description="List of areas to develop"
    )


class ExperienceBenchmarkRaw(BaseModel):
    your_experience_years: str
    typical_for_target_role_years: str = Field(
        ...,
        description="Typical experience years for the target role",
        examples=["3-5", "5-7", "7-10", "0-1", "1-3", "10+"],
    )
    gap_analysis: str


class InterviewReadinessRaw(BaseModel):
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


class QuickWinRaw(BaseModel):
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


class PeerComparisonMetricsRaw(BaseModel):
    profile_strength_percent: int = Field(
        ..., ge=0, le=100, description="Profile strength percentage"
    )
    better_than_peers_percent: int = Field(
        ..., ge=0, le=100, description="Percentage better than peers"
    )


class PeerComparisonRaw(BaseModel):
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
    summary: str
    metrics: PeerComparisonMetricsRaw


class SuccessLikelihoodRaw(BaseModel):
    score_percent: int
    notes: str


class ProfileEvaluationRaw(BaseModel):
    profile_strength_score: int = Field(
        ..., ge=0, le=100, description="Overall profile score from 0 to 100"
    )
    profile_strength_notes: str

    # Current profile summary (for Career Transition section)
    current_profile: CurrentProfileSummaryRaw = Field(
        ..., description="Detailed summary of user's current profile based on quiz responses"
    )

    skill_analysis: SkillAnalysisRaw
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

    experience_benchmark: ExperienceBenchmarkRaw
    interview_readiness: InterviewReadinessRaw
    peer_comparison: PeerComparisonRaw
    success_likelihood: SuccessLikelihoodRaw

    quick_wins: List[QuickWinRaw] = Field(
        ...,
        min_length=3,
        description="List of quick wins to improve profile with title and description, don't mention any specific online course name"
    )
    opportunities_you_qualify_for: List[str] = Field(
        ...,
        min_length=0,
        description="List of job opportunities you currently qualify for"
    )
    recommended_roles_based_on_interests: List[RecommendedRoleRaw]

    badges: List[str]


class FullProfileEvaluationResponseRaw(BaseModel):
    profile_evaluation: ProfileEvaluationRaw
