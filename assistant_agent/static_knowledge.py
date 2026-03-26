# Local Knowledge Base for Offline Resilience
# Providing value even when APIs are down.

CAREER_SENSE = {
    "cloud": "Focus on AWS/GCP certifications, IaC (Terraform), and Kubernetes orchestration.",
    "ai": "Master Python, PyTorch/TensorFlow, and RAG architectures for LLMs.",
    "software": "Clean code, Design Patterns, and System Design are your strongest assets.",
    "generic": "Stay curious, build consistent projects, and network with industry leaders."
}

PRODUCTIVITY_HACKS = [
    "Use the Pomodoro technique: 25 mins work, 5 mins break.",
    "Eat the frog: Handle your most difficult task first thing in the morning.",
    "Time blocking: Schedule specific blocks for deep work without distractions.",
    "Inbox Zero: Process your emails at set times rather than checking constantly."
]

def get_emergency_wisdom(query: str):
    query = query.lower()
    for key, wisdom in CAREER_SENSE.items():
        if key in query:
            return f"💡 **Local Insight**: {wisdom}"
    return f"🚀 **Quick Tip**: {PRODUCTIVITY_HACKS[0]}"
