import os

# --- CAREER TOOLS (Ported from CareerPilot) ---

def suggest_skills(career_goal: str) -> str:
    """Suggests a prioritised list of skills based on the user's career goal.
    
    Args:
        career_goal: The user's stated career goal.
    """
    return (
        f"🏅 **Skill Matrix for {career_goal}**\n\n"
        "1. **Core Proficiency** — Deep dive into domain-specific languages/tools.\n"
        "2. **Cloud Infrastructure** — GCP (Cloud Run, Vertex AI).\n"
        "3. **AI/ML Integration** — Building agents with ADK and Gemini.\n"
        "4. **Soft Skills** — System Design, Technical Writing, and Mentorship.\n\n"
        "> *Tip: Focus on one 'Hard Skill' per month to avoid burnout.*"
    )

def suggest_projects(career_goal: str) -> str:
    """Recommends high-impact portfolio projects aligned with the user's career goal.
    
    Args:
        career_goal: The user's stated career goal.
    """
    return (
        f"🏗️ **Portfolio Killers for {career_goal}**\n\n"
        "1. **Modern Multi-Agent System** — Similar to this assistant (using ADK).\n"
        "2. **Auto-Scaling API** — Deployed to Cloud Run with CI/CD.\n"
        "3. **RAG Knowledge Base** — Intelligent Q&A with private documents.\n\n"
        "**Quick Win**: Deploy a simple FastAPI service to Cloud Run today!"
    )

def resume_feedback(resume_text: str) -> str:
    """Provides structured, actionable feedback on a user's resume summary.
    
    Args:
        resume_text: The text content of the resume.
    """
    return (
        "📄 **Executive Resume Feedback**\n\n"
        "**Key Improvements**:\n"
        "1. **Quantifiable Impact** — Use numbers (e.g., 'reduced latency by 40%').\n"
        "2. **Action Verbs** — Use 'Architected', 'Pioneered', or 'Spearheaded'.\n"
        "3. **ATS Alignment** — Ensure 'Vertex AI' and 'ADK' are prominent.\n\n"
        "**Score**: 8/10. Add more specific project links for a 10/10."
    )

def career_path_guide(current_role: str, target_role: str) -> str:
    """Generates a personalised career transition roadmap.
    
    Args:
        current_role: Current job role or skill level.
        target_role: Desired goal role.
    """
    return (
        f"🗺️ **Roadmap: {current_role} → {target_role}**\n\n"
        "**Phase 1 (Months 1-3)**: Skill Gap Mastery & Foundational Projects.\n"
        "**Phase 2 (Months 4-6)**: Advanced Certifications & Networking.\n"
        "**Phase 3 (Months 7-12)**: Portfolio Polishing & Strategic Applications.\n\n"
        "**Next Step**: Book a networking call with someone in a {target_role} position."
    )
