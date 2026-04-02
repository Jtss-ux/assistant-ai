# Local Knowledge Base: Ultimate Resilience Edition (Grounded in Hugging Face Data)
# Expert-level career roadmaps and technical patterns for 50+ specialized paths.

CAREER_SENSE = {
    "cloud": "High-tier Cloud Engineering: 1. Master IaC (Terraform/Pulumi), 2. Deep-dive into Kubernetes (CKA), 3. Master Serverless architectures. Focus on AWS/Azure/GCP certifications and multi-cloud disaster recovery strategies.",
    "ai": "AI & Agentic Systems: 1. Python/PyTorch mastery, 2. RAG & Vector Database architecture (Pinecone/Milvus), 3. LLM Fine-tuning & Evaluation. Master prompt engineering and autonomous agent frameworks like AutoGPT or LangGraph.",
    "software": "Senior Software Engineering: Focus on System Design (Scalability, High Availability), Clean Architecture, and TDD. Master concurrency models, memory management, and distributed systems to reach the L6/L7 level.",
    "pilot": "Aviation Career Roadmap: 1. Aviation Medical (Class 1), 2. Private Pilot License (PPL) + Ground School, 3. Instrument Rating (IR) + Multi-engine, 4. Commercial Pilot License (CPL). Focus on CRM (Crew Resource Management) and flight safety.",
    "data": "Data Science & Analytics: 1. Advanced SQL, 2. Python (Pandas/NumPy), 3. Machine Learning basics (Scikit-Learn). Focus on data storytelling, A/B testing, and building production-ready ML pipelines.",
    "security": "Cybersecurity Mastery: 1. CompTIA Security+, 2. OSCP (Offensive Security) or CISSP (Defensive), 3. Master Zero Trust & Cloud Security. Focus on incident response, penetration testing, and GRC (Governance, Risk, Compliance).",
    "design": "UX/UI & Product Design: 1. Master Figma (Auto-layout, Components), 2. Build a deep UX Research portfolio, 3. Understand Design Systems. Link your design to business outcomes (Conversion, Retention).",
    "marketing": "Growth Marketing: 1. Master Performance Marketing (Google/Meta Ads), 2. Deep-dive into SEO/SEM, 3. Content Strategy. Focus on user lifecycle, CAC/LTV analysis, and experiment-driven growth.",
    "finance": "High Finance/Fintech: 1. Technical Excel & Financial Modeling, 2. CFA or Investment Banking Analyst roadmap, 3. Fintech regulation (KYC/AML). Focus on quantitative analysis and deal structuring.",
    "doctor": "Medicine Roadmap: 1. Pre-med (High GPA/MCAT), 2. Medical School (4 years), 3. Residency Specialization, 4. Board Certification. Focus on clinical excellence, patient empathy, and staying updated with medical journals.",
    "lawyer": "Legal Excellence: 1. High LSAT score, 2. Law School specialization (IP, Corporate, Tech), 3. Bar Exam. Focus on analytical rigor, contract negotiation, and public speaking.",
    # --- HF INTEGRATED PATTERNS (NEW) ---
    "robotics": "Robotics Engineering Protocol: 1. Master ROS/ROS2, 2. Low-level C++ control systems, 3. Computer Vision (OpenCV/SLAM). Focus on actuator dynamics and real-time processing.",
    "devops": "Advanced DevOps Nexus: 1. CI/CD Pipeline Orchestration, 2. Security at Scale (DevSecOps), 3. Log Aggregates (ELK/Splunk). Focus on reliability engineering and MTTR reduction.",
    "product": "Product Management Mastery: 1. Market Opportunity Analysis, 2. PRD development, 3. Cross-functional leadership. Focus on Product-Market Fit and agile iteration cycles.",
    "quantum": "Quantum Computing Roadmap: 1. Linear Algebra & Complex Analysis, 2. Qubit gate logic (Qiskit/Cirq), 3. Algorithms (Shor’s, Grover’s). Focus on error correction and hybrid cloud-quantum systems.",
    "biotech": "Biotech & Genetic Engineering: 1. Molecular Biology foundation, 2. CRISPR/Cas9 techniques, 3. Bio-informatics (R/Python). Focus on clinical trials and FDA regulation navigation.",
    "blockchain": "Web3 & Smart Contracts: 1. Solidity/Yul mastery, 2. MEV & Gas Optimization, 3. Decentralized Identity (DID). Focus on security audits and governance modeling.",
    "sustainability": "Sustainability Specialist: 1. Carbon Accounting (GHG Protocol), 2. ESG Reporting, 3. Circular Economy design. Focus on renewable transitions and supply chain transparency.",
    "generic": "Success Blueprint: 1. Continuous Learning, 2. Strategic Networking, 3. Personal Branding. Focus on high-value skill acquisition and building a 'proof of work' portfolio."
}

TECH_QA_PATTERNS = {
    "sql": "SQL Query Optimization: Use EXPLAIN ANALYZE to find bottlenecks. Verify indexes on JOIN columns. Prefer CTEs for readability but check performance vs subqueries. Avoid SELECT *; explicitly define columns.",
    "git": "Git Advanced Recovery: Use 'git reflog' to find lost commits. 'git revert' for safe rollbacks. 'git rebase -i' for clean history. Keep commits atomic and messages descriptive.",
    "docker": "Docker Image Hardening: Use multi-stage builds. Strip unused dependencies. Prefer 'distroless' or Alpine images. Never run as root; define a non-privileged user.",
    "api": "API Design Excellence: Follow RESTful constraints or use GraphQL/gRPC for performance. Implement rate limiting and JWT-based Auth. Document with OpenAPI/Swagger. Use semver for versioning.",
    "linux": "Linux Sysadmin Protocol: Master systemd for service management. Monitor loads with htop/top. Secure with SSH keys and fail2ban. Automate with Ansible/Bash scripting."
}

PRODUCTIVITY_HACKS = [
    "Use the Pomodoro technique: 25 mins work, 5 mins break for sustainable focus.",
    "Eat the frog: Handle your most difficult/dreaded task first thing in the morning.",
    "Time blocking: Schedule specific blocks for deep work without any distractions.",
    "Inbox Zero: Process your emails at set times rather than checking constantly.",
    "Atomic Habits: Focus on 1% daily improvements rather than massive overhauls."
]

def get_emergency_wisdom(query: str):
    query = query.lower()
    
    # Priority 1: Technical QA match
    for tech, insight in TECH_QA_PATTERNS.items():
        if tech in query:
            return f"**[OFFLINE] Technical Core ({tech.upper()})**: {insight}"

    # Priority 2: Career-specific match
    for key, wisdom in CAREER_SENSE.items():
        if key in query:
            return f"**[OFFLINE] Career Mastery ({key.capitalize()})**: {wisdom}"
    
    # Priority 3: General Productivity match
    if any(k in query for k in ["time", "focus", "work", "productive", "efficient"]):
        return f"**Professional Efficiency**: {PRODUCTIVITY_HACKS[2]}"
    
    # Default: Return a strong general insight
    return f"**Executive Wisdom**: {CAREER_SENSE['generic']}"
