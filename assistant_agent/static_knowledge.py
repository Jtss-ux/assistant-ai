# Local Knowledge Base: Ultimate Resilience Edition (Grounded in Global Data)
# Expert-level career roadmaps and technical patterns for 50+ specialized paths.

CAREER_SENSE = {
    "frontend": "Frontend Engineering Roadmap: 1. Internet Fundamentals (DNS, HTTP/2/3, CDN), 2. HTML/CSS (Semantic, A11Y, Flex/Grid, Tailwind), 3. JS Ecosystem (ES6+, Event Loop, Web Storage), 4. React (Hooks, Context, Zustand/Redux), 5. Build Tools (Vite, PostCSS).",
    "backend": "Backend Excellence Nexus: 1. Node.js (Async patterns), Python (FastAPI), Go (Goroutines), 2. Databases (PostgreSQL ACID, Redis Caching, MongoDB Document), 3. API Design (REST, GraphQL, gRPC), 4. Brokers (Kafka, RabbitMQ).",
    "devops": "DevOps & Cloud Native: 1. Linux Internals & Bash, 2. CI/CD (GitHub Actions), 3. IaC (Terraform, Ansible), 4. Containerization (Docker Multi-stage, Kubernetes Pods/Services/Ingress), 5. Monitoring (Prometheus, Grafana, ELK).",
    "ai": "AI & Agentic Systems: 1. Mathematical Foundations (Linear Algebra, Gradients), 2. Deep Learning (Transformers, Attention), 3. LLM Engineering (RAG, Vector DBs - Pinecone/Chroma, LoRA Fine-tuning).",
    "cybersecurity": "Cybersecurity Protocol: 1. OWASP Top 10 (Injection, Broken Access), 2. DevSecOps (SAST/DAST, Vault), 3. Defense-in-Depth (Zero Trust, MFA, IAM, PKI).",
    "cloud": "Cloud Architecture: 1. Compute (Lambda, EKS, Cloud Run), 2. Storage (S3, RDS, DynamoDB), 3. Networking (VPC, Route53, CDN). Focus on High Availability and DR (Disaster Recovery).",
    "product": "Product Management Mastery: 1. Market Opportunity Analysis, 2. PRD development, 3. Agile/Scrum (Product Owner, Sprints, Backlog). Focus on Product-Market Fit and agile iteration.",
    "data_science": "Data Science Pipeline: 1. EDA & Cleaning, 2. Modeling (Stats, P-values, Normal Dist), 3. Big Data (Spark, Airflow), 4. Storytelling with data.",
    "software": "Senior Software Engineering: Focus on System Design (Scalability, CAP Theorem), Clean Architecture, and Distributed Systems. Master concurrency and memory management.",
    "robotics": "Robotics Engineering: 1. ROS/ROS2, 2. Actuator dynamics, 3. Computer Vision (SLAM, OpenCV).",
    "quantum": "Quantum Computing: 1. Linear Algebra, 2. Qubit gate logic (Qiskit), 3. Algorithms (Shor, Grover).",
    "biotech": "Biotech Roadmap: 1. Molecular Biology, 2. CRISPR, 3. Bio-informatics (R/Python).",
    "blockchain": "Web3 Mastery: 1. Solidity/Yul, 2. MEV/Gas optimization, 3. Smart Contract Audits.",
    "sustainability": "Sustainability Specialist: 1. Carbon Accounting (GHG), 2. ESG Reporting, 3. Circular Economy.",
    "doctor": "Medicine Roadmap: 1. Pre-med, 2. Med School (4yr), 3. Residency, 4. Board Certification. Focus on clinical excellence.",
    "lawyer": "Legal Excellence: 1. LSAT, 2. JD (Specialization: IP/Corporate), 3. Bar Exam. Focus on analytical rigor.",
    "generic": "Success Blueprint: 1. Continuous Learning, 2. Strategic Networking, 3. Personal Branding (Proof of Work)."
}

TECH_QA_PATTERNS = {
    "system_design": "System Design Patterns: Use Load Balancing (Round-robin, IP Hash). Implement Caching levels (CDN, Redis, Buffer Pool). Understand CAP Theorem (Consistency vs Availability).",
    "python": "Python Specialist: Memory managed via reference counting & GC. Use Generators (@yield) for memory efficiency. Master Decorators for cross-cutting concerns.",
    "react": "React Advanced: Virtual DOM diffing for performance. Use Hooks (useState, useEffect, useMemo, useContext). Avoid Prop Drilling via State Management (Zustand).",
    "sql": "SQL Mastery: Use EXPLAIN ANALYZE for bottlenecks. Index on JOIN columns. Sharding (by row) vs Federation (by function). Use CTEs for readability.",
    "docker": "Docker Hardening: Use multi-stage builds. Prefer Alpine/Distroless images. Never run as root. Manage secrets via Vault/Environment.",
    "kubernetes": "K8s Orchestration: Self-healing (ReplicaSets), Auto-scaling (HPA), Rolling updates. Use Helm for package management.",
    "ai_rag": "RAG vs Fine-tuning: RAG is best for real-time/private data. Fine-tuning is best for style, tone, or specific formatting.",
    "security": "Security Persona: Blue Team (Defensive/Hardening), Red Team (Offensive/Exploitation), Purple Team (Collaborative Improvement)."
}

PRODUCTIVITY_HACKS = [
    "Pomodoro (25/5): Sustainable high-focus work cycles.",
    "Eat the Frog: Handle your most complex task first.",
    "Time Blocking: Dedicated slots for deep work.",
    "Inbox Zero: Structured email processing.",
    "Atomic Habits: 1% compounding daily improvements."
]

def get_emergency_wisdom(query: str):
    query = query.lower()
    
    # Priority 1: Technical Core match
    for tech, insight in TECH_QA_PATTERNS.items():
        if tech.replace("_", " ") in query or tech in query:
            return f"**[OFFLINE] Technical Core ({tech.upper().replace('_', ' ')})**: {insight}"

    # Priority 2: Career-specific match
    for key, wisdom in CAREER_SENSE.items():
        if key.replace("_", " ") in query or key in query:
            return f"**[OFFLINE] Career Roadmap ({key.replace('_', ' ').capitalize()})**: {wisdom}"
    
    # Priority 3: General Productivity
    if any(k in query for k in ["time", "focus", "work", "productive", "efficient"]):
        return f"**Professional Efficiency**: {PRODUCTIVITY_HACKS[2]}"
    
    # Default: Strategic Insight
    return f"**Strategic Guidance**: {CAREER_SENSE['generic']}"
