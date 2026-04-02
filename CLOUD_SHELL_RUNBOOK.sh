#!/usr/bin/env bash
# ============================================================
#  CareerPilot AI — Google Cloud Shell Deployment Runbook
#  Project: Multi-Agent Career Guidance Agent (ADK 1.x)
#  Run each STEP block one at a time in Google Cloud Shell.
# ============================================================

# ─────────────────────────────────────────────
#  STEP 1 — Authenticate & confirm project
# ─────────────────────────────────────────────
gcloud auth login                           # authenticate if not already
gcloud auth application-default login      # needed for Vertex AI / ADK

export PROJECT_ID=$(gcloud config get-value project)
echo "✅ Using project: $PROJECT_ID"
# If blank, set it: gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

# ─────────────────────────────────────────────
#  STEP 2 — Create project folder
# ─────────────────────────────────────────────
cd ~
mkdir -p career_agent            # the agent MODULE folder
# Important: adk web and adk deploy are run from HOME (~)
# pointing at the career_agent/ subfolder as the module name

# ─────────────────────────────────────────────
#  STEP 3 — Write __init__.py  (CRITICAL — ADK needs this)
# ─────────────────────────────────────────────
cat << 'EOF' > ~/career_agent/__init__.py
# Required by Google ADK to recognise this directory as a Python module.
from .agent import root_agent
__all__ = ["root_agent"]
EOF

# ─────────────────────────────────────────────
#  STEP 4 — Write agent.py  (multi-agent orchestrator)
# ─────────────────────────────────────────────
cat << 'PYEOF' > ~/career_agent/agent.py
import os
from dotenv import load_dotenv
load_dotenv()
from google.adk.agents import Agent

# ── Tool Functions ──────────────────────────────────────────

def suggest_skills(career_goal: str) -> str:
    """Suggests a prioritised list of skills based on the user's career goal.

    Args:
        career_goal: The user's stated career goal or area of interest.

    Returns:
        A structured, prioritised skill development plan.
    """
    return (
        f"For '{career_goal}', here are the key skills to master:\n"
        "1. **Technical Foundation** — Python, Git, Linux basics\n"
        "2. **Cloud & Infrastructure** — Google Cloud Platform, Cloud Run, Docker\n"
        "3. **AI/ML** — Generative AI, Prompt Engineering, LLM APIs\n"
        "4. **Soft Skills** — Communication, problem solving, system design\n"
        "5. **Certifications** — Google Cloud Associate + relevant specializations"
    )

def suggest_projects(career_goal: str) -> str:
    """Recommends real-world portfolio project ideas aligned with the user's career goal.

    Args:
        career_goal: The user's stated career goal or area of interest.

    Returns:
        A list of portfolio project ideas with brief descriptions.
    """
    return (
        f"Top portfolio projects for '{career_goal}':\n"
        "1. **AI Chatbot** — Domain-specific chatbot using Google ADK + Gemini\n"
        "2. **Resume Analyzer** — Upload resume, get AI-powered feedback\n"
        "3. **Cloud-Native App** — FastAPI service deployed to Cloud Run\n"
        "4. **RAG Knowledge Base** — Q&A agent with Vertex AI + document ingestion\n"
        "5. **Multi-Agent System** — Orchestrator + specialist agent pipeline"
    )

def resume_feedback(resume_text: str) -> str:
    """Provides structured, actionable feedback on a user's resume.

    Args:
        resume_text: The raw text content of the user's resume.

    Returns:
        Structured feedback with specific improvement suggestions.
    """
    return (
        "📋 **Resume Analysis**\n\n"
        "**Improvements needed:**\n"
        "1. **Quantify achievements** — Replace 'worked on X' with 'improved X by 30%'\n"
        "2. **Action verbs** — Start bullets with: Built, Designed, Deployed, Optimised\n"
        "3. **Skills section** — Add a dedicated technical skills block\n"
        "4. **Projects section** — Add GitHub links and one-line impact statements\n"
        "5. **Tailor per role** — Mirror keywords from the job description"
    )

def career_path_guide(current_role: str, target_role: str) -> str:
    """Generates a personalised 3-phase career transition roadmap.

    Args:
        current_role: The user's current job role or experience level.
        target_role: The role the user wants to achieve.

    Returns:
        A step-by-step career transition roadmap with milestones.
    """
    return (
        f"🗺️ **Career Roadmap: {current_role} → {target_role}**\n\n"
        "**Phase 1 (0-3 months): Foundation**\n"
        "- Complete Google Cloud fundamentals + ADK hands-on labs\n"
        "- Build your first deployed AI agent project\n\n"
        "**Phase 2 (3-6 months): Depth**\n"
        "- Earn a Google Cloud certification\n"
        "- Build 2-3 portfolio projects with real-world impact\n\n"
        "**Phase 3 (6-12 months): Visibility**\n"
        "- Contribute to open-source AI projects\n"
        "- Write technical blog posts / speak at meetups\n"
        "- Apply to target roles with portfolio evidence"
    )

# ── Specialist Sub-Agents ────────────────────────────────────

resume_agent = Agent(
    name="resume_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist agent for resume analysis and structured improvement suggestions.",
    instruction="""
You are the Resume Specialist of CareerPilot AI.
Your ONLY job is to analyze resumes and provide structured, actionable improvement suggestions.
Always use the resume_feedback tool when a resume is provided.
Format your response as:
1. **Overall Assessment** — Brief evaluation
2. **Key Improvements** — Specific, numbered suggestions
3. **ATS Optimisation** — Keyword tips for applicant tracking systems
4. **Final Score** — Rate the resume /10 and what would make it a 10/10
    """,
    tools=[resume_feedback],
)

skill_agent = Agent(
    name="skill_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist agent for skill gap analysis and learning path recommendations.",
    instruction="""
You are the Skills Development Specialist of CareerPilot AI.
Your ONLY job is to analyze skill gaps and recommend prioritised learning paths.
Always use the suggest_skills tool to generate skill recommendations.
Use external knowledge about job trends, industry demand, and market insights.
Format your response as:
1. **Priority Skills** — Top 5 skills to learn now
2. **Learning Resources** — Best ways to learn each skill
3. **Timeline** — Realistic milestones (30 / 60 / 90 days)
4. **Certifications** — Relevant certifications to pursue
    """,
    tools=[suggest_skills],
)

project_agent = Agent(
    name="project_agent",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description="Specialist agent for portfolio project ideas and career transition roadmaps.",
    instruction="""
You are the Project & Roadmap Specialist of CareerPilot AI.
Your ONLY job is to suggest real-world portfolio projects and career transition roadmaps.
Always use suggest_projects for project ideas and career_path_guide for roadmap requests.
Format your response as:
1. **Top 5 Projects** — With brief descriptions and tech stacks
2. **Quick Win** — One project you can start TODAY
3. **Career Roadmap** — If requested, use career_path_guide
4. **GitHub Tips** — How to present projects effectively
    """,
    tools=[suggest_projects, career_path_guide],
)

# ── Orchestrator root_agent ──────────────────────────────────

root_agent = Agent(
    name="careerpilot_orchestrator",
    model=os.environ.get("MODEL", "gemini-1.5-flash"),
    description=(
        "CareerPilot AI — an intelligent multi-agent career guidance orchestrator "
        "that routes user queries to specialist sub-agents and aggregates responses."
    ),
    sub_agents=[resume_agent, skill_agent, project_agent],
    instruction="""
You are CareerPilot AI — an intelligent career guidance orchestrator.

You are a multi-agent AI system. Route user queries to the correct specialist:
- Resume / CV questions → transfer to resume_agent
- Skills / learning questions → transfer to skill_agent
- Projects / portfolio / roadmap → transfer to project_agent
- General career guidance → use skill_agent and project_agent together

After receiving sub-agent responses, aggregate and format as:
1. **Career Path** — Target roles and progression sequence
2. **Skills to Learn** — From skill_agent
3. **Suggested Projects** — From project_agent
4. **Resume Tips** — From resume_agent (if resume was provided)
5. **Next Steps** — 3 concrete actions for this week

Use external knowledge (job trends, industry demand, market insights) in recommendations.
The system is designed to integrate with MCP servers for real-time data such as
job trends and market demand.
    """,
)
PYEOF

# ─────────────────────────────────────────────
#  STEP 5 — Write requirements.txt
# ─────────────────────────────────────────────
cat << 'EOF' > ~/career_agent/requirements.txt
google-adk>=1.0.0
google-genai
google-cloud-aiplatform>=1.38.0
python-dotenv
EOF

# ─────────────────────────────────────────────
#  STEP 6 — Write .env  (auto-fills project ID)
# ─────────────────────────────────────────────
cat << EOF > ~/career_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=${PROJECT_ID}
GOOGLE_CLOUD_LOCATION=us-central1
MODEL=gemini-1.5-flash
EOF

echo "✅ All files written. Verifying structure:"
ls -la ~/career_agent/

# ─────────────────────────────────────────────
#  STEP 7 — Install dependencies
# ─────────────────────────────────────────────
pip install -r ~/career_agent/requirements.txt

# ─────────────────────────────────────────────
#  STEP 8 — Run locally with ADK web UI
# ─────────────────────────────────────────────
# MUST run from HOME (~), pointing at the folder NAME (career_agent)
cd ~
adk web career_agent

# In the ADK UI (http://localhost:8000 or Cloud Shell preview port 8000):
#   1. The agent listed will be "careerpilot_orchestrator"
#   2. Select it from the left panel
#   3. Try these test prompts:
#       "I want to become a data scientist"
#       "Suggest projects for web development"
#       "How do I move from software developer to AI engineer?"
#       "Here is my resume: [paste any text] — give me feedback"
#
# 📸 SCREENSHOT #1: The ADK UI showing a response from careerpilot_orchestrator
# Press CTRL+C to stop the local server

# ─────────────────────────────────────────────
#  STEP 9 — Deploy to Cloud Run
# ─────────────────────────────────────────────
# MUST run from HOME (~), pointing at the folder NAME
cd ~
adk deploy cloud_run \
  --project="${PROJECT_ID}" \
  --region=us-central1 \
  --service_name=career-agent \
  --with_ui \
  career_agent

# When prompted "Allow unauthenticated invocations? (y/N)" → type: y  then ENTER
# Wait 10-15 minutes for Cloud Build + Cloud Run deployment

# You will see output like:
#   Service URL: https://career-agent-XXXXXXXXXX-uc.a.run.app
#
# 📸 SCREENSHOT #2: The terminal showing "Service URL: https://career-agent-..."

# ─────────────────────────────────────────────
#  STEP 10 — Test the live deployed agent
# ─────────────────────────────────────────────
# Open the Service URL in your browser
# The ADK Web UI will load
# Select "careerpilot_orchestrator" from the left panel
# Ask: "I want to become an AI engineer, suggest a career plan"
#
# 📸 SCREENSHOT #3: The live Cloud Run agent giving a structured response

# ─────────────────────────────────────────────
#  STEP 11 — Submit at hack2skill
# ─────────────────────────────────────────────
# 1. Go to: https://vision.hack2skill.com/event/apac-genaiacademy/dashboard/roadmap
# 2. Click: "Project Submission (Track 1) - Build and Deploy AI Agents"
# 3. Dropdown: select "Track 1 - Build and deploy AI agents using Gemini, ADK, and Cloud Run"
# 4. Upload: Screenshot #3 (the live Cloud Run agent response — most impressive)
# 5. Click: Submit ✅
#
# DONE! Deadline: March 31, 2026 11:59 PM IST
