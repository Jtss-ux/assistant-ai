# Local Knowledge Base: Premium Offline Edition
# Providing deep, relevant value even when APIs are down.

CAREER_SENSE = {
    "cloud": "Focus on AWS/GCP certifications, IaC (Terraform), and Kubernetes orchestration. Master serverless and edge computing for modern high-scale apps.",
    "ai": "Master Python, PyTorch/TensorFlow, RAG architectures, and fine-tuning LLMs. Understand the ethics and deployment of agents.",
    "software": "Clean code, Design Patterns, and System Design are your strongest assets. Focus on performance, scalability, and test-driven development.",
    "pilot": "Becoming a Pilot requires clear milestones: 1. Obtain a Class 1 Medical, 2. Compete Ground School (PPL), 3. Accumulate Flight Hours, 4. Earn CPL/ATPL licenses. Focus on cockpit discipline and navigation.",
    "data": "Master SQL, Python, and visualization tools like Tableau. Understand statistical modeling and predictive analytics for business transformation.",
    "security": "Focus on CompTIA Security+, CISSP, and offensive/defensive strategies. Master Zero-Trust architecture and incident response protocols.",
    "design": "Master Figma/Adobe Suite. Focus on UX research, design systems, and prototyping. Understanding frontend code makes you a 10x designer.",
    "marketing": "Master SEO, SEM, and data-driven growth strategies. Focus on customer psychology, conversion funnel optimization, and brand storytelling.",
    "finance": "Master Financial Modeling, Excel, and CFA concepts. Understand risk management and quantitative analysis for investment banking or fintech.",
    "doctor": "Medicine is a marathon: 1. Undergraduate (Pre-med), 2. Medical School (MCAT), 3. Residency specialization, 4. Board Certification. Focus on empathy and life-long learning.",
    "writer": "Consistency is key. Build a public portfolio (Substack/Medium), master SEO-driven copywriting, and develop a unique voice to stand out in the AI era.",
    "lawyer": "Focus on LSAT preparation, choosing a niche (Corporate, Tech, IP), and building strong analytical and advocacy skills. Bar exam is your final hurdle.",
    "entrepreneur": "Focus on 'Zero to One' thinking. Build an MVP, validate with real users, and understand unit economics before scaling. Network is your net worth.",
    "fullstack": "Master both frontend (React/Next) and backend (Node/Python). Focus on database design (SQL/NoSQL) and cloud deployment (Docker/GCP).",
    "mobile": "Choose between Native (Swift/Kotlin) or Cross-platform (Flutter/React Native). Master mobile UX constraints and App Store deployment workflows.",
    "generic": "Stay curious, build consistent projects, and network with industry leaders. Focus on continuous improvement and personal branding."
}

PRODUCTIVITY_HACKS = [
    "Use the Pomodoro technique: 25 mins work, 5 mins break for sustainable focus.",
    "Eat the frog: Handle your most difficult/dreaded task first thing in the morning.",
    "Time blocking: Schedule specific blocks for deep work without any distractions.",
    "Inbox Zero: Process your emails at set times rather than checking constantly.",
    "Atomic Habits: Focus on 1%% daily improvements rather than massive overhauls."
]

def get_emergency_wisdom(query: str):
    query = query.lower()
    
    # Priority 1: Career-specific match
    for key, wisdom in CAREER_SENSE.items():
        if key in query:
            return f"💡 **Career Strategy**: {wisdom}"
    
    # Priority 2: General Productivity match
    if "time" in query or "focus" in query or "work" in query:
        return f"🚀 **Productivity Tip**: {PRODUCTIVITY_HACKS[2]}"
    
    # Default: Return a strong general insight
    return f"🚀 **Executive Tip**: {CAREER_SENSE['generic']}"
