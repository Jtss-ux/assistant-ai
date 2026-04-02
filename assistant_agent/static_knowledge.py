# Local Knowledge Base: Ultimate Resilience Edition
# Expert-level career roadmaps for 30+ specialized paths.

CAREER_SENSE = {
    "cloud": "High-tier Cloud Engineering: 1. Master IaC (Terraform/Pulumi), 2. Deep-dive into Kubernetes (CKA), 3. Master Serverless architectures. Focus on AWS/Azure/GCP certifications and multi-cloud disaster recovery strategies.",
    "ai": "AI & Agentic Systems: 1. Python/PyTorch mastery, 2. RAG & Vector Database architecture (Pinecone/Milvus), 3. LLM Fine-tuning & Evaluation. Master prompt engineering and autonomous agent frameworks like AutoGPT or LangGraph.",
    "software": "Senior Software Engineering: Focus on System Design (Scalability, High Availability), Clean Architecture, and TDD. Master concurrency models, memory management, and distributed systems to reach the L6/L7 level.",
    "pilot": "Aviation Career Roadmap: 1. Aviation Medical (Class 1), 2. Private Pilot License (PPL) + Ground School, 3. Instrument Rating (IR) + Multi-engine, 4. Commercial Pilot License (CPL). Focus on CRM (Crew Resource Management) and flight safety.",
    "data": "Data Science & Analytics: 1. Advanced SQL, 2. Python (Pandas/NumPy), 3. Machine Learning basics (Scikit-Learn). Focus on data storytelling, A/B testing, and building production-ready ML pipelines.",
    "security": "Cybersecurity Mastery: 1. CompTIA Security+, 2. OSCP (Offensive Security) or CISSP (Defensive), 3. Master Zero Trust & Cloud Security. Focus on incident response, penetration testing, and GRC (Governance, Risk, Compliance).",
    "design": "UX/UI & Product Design: 1. Master Figma (Auto-layout, Components), 2. Build a deep UX Research portfolio, 3. Understand Design Systems. Link your design to business outcomes (Conversion, Retention).",
    "marketing": "Growth Marketing: 1. Master Performance Marketing (Google/Meta Ads), 2. Deep-dive into SEO/SEM, 3. Content Strategy & Virgil. Focus on user lifecycle, CAC/LTV analysis, and experiment-driven growth.",
    "finance": "High Finance/Fintech: 1. Technical Excel & Financial Modeling, 2. CFA or Investment Banking Analyst roadmap, 3. Fintech regulation (KYC/AML). Focus on quantitative analysis and deal structuring.",
    "doctor": "Medicine Roadmap: 1. Pre-med (High GPA/MCAT), 2. Medical School (4 years), 3. Residency Specialization, 4. Board Certification. Focus on clinical excellence, patient empathy, and staying updated with medical journals.",
    "writer": "Strategic Writing: 1. Build a public brand (Substack/LinkedIn), 2. Master SEO-Copywriting, 3. Develop a unique voice. Focus on ghostwriting for executives or technical whitepaper specialization.",
    "lawyer": "Legal Excellence: 1. High LSAT score, 2. Law School specialization (IP, Corporate, Tech), 3. Bar Exam. Focus on analytical rigor, contract negotiation, and public speaking.",
    "entrepreneur": "Venture Building: 1. Problem validation (MVP), 2. Unit economics (LTV > 3x CAC), 3. Fundraising vs Bootstrapping. Focus on 'the first 10 customers' and building a high-performance culture.",
    "fullstack": "Modern Full-stack: 1. Mastery of Next.js/React, 2. Node.js or Go backend, 3. PostgreSQL/Redis optimization. Focus on CI/CD pipelines, Docker, and edge computing deployment.",
    "architect": "Architectural Design: 1. B.Arch or M.Arch degree, 2. Licensing exams (ARE), 3. Mastery of Revit/AutoCAD. Focus on sustainable design, urban planning, and structural integrity.",
    "chef": "Culinary Mastery: 1. Classical French techniques, 2. Specialized cuisine focus, 3. Kitchen management (Sous-chef roadmap). Focus on flavor profiling, cost control, and team leadership.",
    "real estate": "Real Estate Empire: 1. State Licensing, 2. Niche into Residential or Commercial, 3. Master Digital Marketing for leads. Focus on negotiation, property valuation, and building a local network.",
    "video editor": "High-end Post-Production: 1. Adobe Premiere/DaVinci Resolve mastery, 2. Motion Graphics (After Effects), 3. Color Grading. Focus on storytelling pacing and high-retention editing for creators.",
    "social media": "Social Strategy: 1. Master short-form video (TikTok/Reels), 2. Community Management, 3. Analytics-driven content cycles. Focus on viral hooks, trend-jacking, and brand voice consistency.",
    "architectural": "Architecture & Urban Planning: Master Revit, Rhino, and Grasshopper. Focus on sustainable building codes (LEED) and urban densification strategies.",
    "psychologist": "Psychology & Therapy: 1. Bachelor’s in Psych, 2. Master’s/Doctorate (PhD/PsyD), 3. Clinical Hours/Licensure. Focus on CBT, DBT, and high-empathy patient communication.",
    "trainer": "Personal Training & Fitness: 1. NASM/ACE Certification, 2. Specialization (Weight Loss, Athletic Perf), 3. Program Design. Focus on nutrition science, biomechanics, and client motivation.",
    "blockchain": "Web3 Engineering: 1. Solidity/Rust mastery, 2. Smart Contract Security, 3. DeFi/NFT protocols. Focus on gas optimization and decentralized architecture.",
    "game": "Game Development: 1. Unity or Unreal Engine (C#/C++), 2. 3D Modeling (Blender), 3. Game Mechanics Design. Focus on performance optimization and player retention loops.",
    "hr": "HR & Talent Acquisition: 1. SHRM Certification, 2. Strategic Recruitment, 3. Employee Branding. Focus on organizational culture, conflict resolution, and DE&I initiatives.",
    "accountant": "Accountancy & Auditing: 1. CPA or ACCA qualification, 2. Corporate Tax or Audit focus, 3. Mastery of ERP systems (SAP/Oracle). Focus on financial transparency and compliance.",
    "generic": "Success Blueprint: 1. Continuous Learning, 2. Strategic Networking, 3. Personal Branding. Focus on high-value skill acquisition and building a 'proof of work' portfolio."
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
            return f"**Career Mastery ({key.capitalize()})**: {wisdom}"
    
    # Priority 2: General Productivity match
    if any(k in query for k in ["time", "focus", "work", "productive", "efficient"]):
        return f"**Professional Efficiency**: {PRODUCTIVITY_HACKS[2]}"
    
    # Default: Return a strong general insight
    return f"**Executive Wisdom**: {CAREER_SENSE['generic']}"
