"""
Seed skill taxonomy — Backend Development vertical.

Module 8: expanded from the original 20-node starter set to 47 nodes,
adding depth in databases, API design, security, system design,
observability, testing, and DevOps — all within the Backend Development
vertical (no unrelated domains added).

Each node's `prerequisites` list must reference IDs defined anywhere in
this file (the list is fully evaluated before SkillGraph reads it, so
order doesn't matter for existence — only cycles matter, and those are
caught by SkillGraph's validation on load).
"""

from app.models.schemas import SkillNode, Resource, ResourceType

SEED_SKILLS: list[SkillNode] = [
    SkillNode(
        id="python_basics",
        name="Python Fundamentals",
        category="programming",
        difficulty_tier=1,
        prerequisites=[],
        resources=[
            Resource(id="r1", title="Python for Everybody", type=ResourceType.COURSE, est_hours=20),
        ],
    ),
    SkillNode(
        id="oop",
        name="Object-Oriented Programming",
        category="programming",
        difficulty_tier=1,
        prerequisites=["python_basics"],
        resources=[
            Resource(id="r2", title="OOP Principles in Python", type=ResourceType.ARTICLE, est_hours=4),
        ],
    ),
    SkillNode(
        id="data_structures",
        name="Data Structures",
        category="programming",
        difficulty_tier=2,
        prerequisites=["python_basics"],
        resources=[
            Resource(id="r3", title="DS in Python", type=ResourceType.COURSE, est_hours=15),
        ],
    ),
    SkillNode(
        id="http_basics",
        name="HTTP & Web Fundamentals",
        category="web",
        difficulty_tier=1,
        prerequisites=[],
        resources=[
            Resource(id="r4", title="How the Web Works", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="rest_apis",
        name="REST API Design",
        category="web",
        difficulty_tier=2,
        prerequisites=["oop", "http_basics"],
        resources=[
            Resource(id="r5", title="Designing RESTful APIs", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="fastapi",
        name="FastAPI Framework",
        category="web",
        difficulty_tier=2,
        prerequisites=["rest_apis"],
        resources=[
            Resource(id="r6", title="FastAPI Official Tutorial", type=ResourceType.COURSE, est_hours=10),
        ],
    ),
    SkillNode(
        id="sql_basics",
        name="SQL Fundamentals",
        category="databases",
        difficulty_tier=1,
        prerequisites=[],
        resources=[
            Resource(id="r7", title="SQL for Beginners", type=ResourceType.COURSE, est_hours=10),
        ],
    ),
    SkillNode(
        id="relational_db_design",
        name="Relational Database Design",
        category="databases",
        difficulty_tier=2,
        prerequisites=["sql_basics"],
        resources=[
            Resource(id="r8", title="DB Normalization & Schema Design", type=ResourceType.ARTICLE, est_hours=5),
        ],
    ),
    SkillNode(
        id="orm",
        name="ORMs (SQLAlchemy)",
        category="databases",
        difficulty_tier=2,
        prerequisites=["relational_db_design", "oop"],
        resources=[
            Resource(id="r9", title="SQLAlchemy Crash Course", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="auth",
        name="Authentication & Authorization (JWT/OAuth)",
        category="security",
        difficulty_tier=3,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r10", title="JWT Auth in FastAPI", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="testing",
        name="API Testing (pytest)",
        category="quality",
        difficulty_tier=2,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r11", title="Testing FastAPI Apps", type=ResourceType.ARTICLE, est_hours=4),
        ],
    ),
    SkillNode(
        id="docker",
        name="Containerization (Docker)",
        category="devops",
        difficulty_tier=2,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r12", title="Docker for Backend Devs", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="caching",
        name="Caching Strategies (Redis)",
        category="performance",
        difficulty_tier=3,
        prerequisites=["orm", "docker"],
        resources=[
            Resource(id="r13", title="Redis Caching Patterns", type=ResourceType.ARTICLE, est_hours=4),
        ],
    ),
    SkillNode(
        id="async_programming",
        name="Async Programming (asyncio)",
        category="programming",
        difficulty_tier=3,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r14", title="Async Python Deep Dive", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="message_queues",
        name="Message Queues (RabbitMQ/Kafka)",
        category="distributed-systems",
        difficulty_tier=4,
        prerequisites=["async_programming", "docker"],
        resources=[
            Resource(id="r15", title="Intro to Message Queues", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="system_design_basics",
        name="System Design Fundamentals",
        category="architecture",
        difficulty_tier=3,
        prerequisites=["rest_apis", "relational_db_design"],
        resources=[
            Resource(id="r16", title="System Design Primer", type=ResourceType.ARTICLE, est_hours=10),
        ],
    ),
    SkillNode(
        id="scalability",
        name="Scalability & Load Balancing",
        category="architecture",
        difficulty_tier=4,
        prerequisites=["system_design_basics", "caching"],
        resources=[
            Resource(id="r17", title="Scaling Backend Systems", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="ci_cd",
        name="CI/CD Pipelines",
        category="devops",
        difficulty_tier=3,
        prerequisites=["docker", "testing"],
        resources=[
            Resource(id="r18", title="GitHub Actions CI/CD", type=ResourceType.COURSE, est_hours=5),
        ],
    ),
    SkillNode(
        id="cloud_deployment",
        name="Cloud Deployment (AWS)",
        category="devops",
        difficulty_tier=3,
        prerequisites=["docker", "ci_cd"],
        resources=[
            Resource(id="r19", title="Deploying to AWS", type=ResourceType.COURSE, est_hours=10),
        ],
    ),
    SkillNode(
        id="microservices",
        name="Microservices Architecture",
        category="architecture",
        difficulty_tier=5,
        # Module 8: added event_driven_architecture, database_sharding, and
        # kubernetes_basics as additional prerequisites now that the graph
        # has depth to support them.
        prerequisites=[
            "scalability", "message_queues", "cloud_deployment",
            "event_driven_architecture", "database_sharding", "kubernetes_basics",
        ],
        resources=[
            Resource(id="r20", title="Microservices in Practice", type=ResourceType.COURSE, est_hours=12),
        ],
    ),

    # -----------------------------------------------------------------
    # Module 8 additions below — databases, API design, security,
    # system design, observability, testing, DevOps (27 new nodes)
    # -----------------------------------------------------------------

    # --- Databases ---
    SkillNode(
        id="indexing_strategies",
        name="Database Indexing Strategies",
        category="databases",
        difficulty_tier=2,
        prerequisites=["relational_db_design"],
        resources=[
            Resource(id="r21", title="Indexing for Performance", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="query_optimization",
        name="Query Optimization",
        category="databases",
        difficulty_tier=3,
        prerequisites=["indexing_strategies"],
        resources=[
            Resource(id="r22", title="SQL Query Optimization Deep Dive", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="db_migrations",
        name="Database Migrations",
        category="databases",
        difficulty_tier=2,
        prerequisites=["orm"],
        resources=[
            Resource(id="r23", title="Managing Schema Migrations", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="nosql_fundamentals",
        name="NoSQL Fundamentals (MongoDB)",
        category="databases",
        difficulty_tier=2,
        prerequisites=["sql_basics"],
        resources=[
            Resource(id="r24", title="MongoDB Basics", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="transactions_acid",
        name="Transactions & ACID Properties",
        category="databases",
        difficulty_tier=2,
        prerequisites=["relational_db_design"],
        resources=[
            Resource(id="r25", title="Understanding ACID", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="connection_pooling",
        name="Connection Pooling",
        category="databases",
        difficulty_tier=3,
        prerequisites=["orm", "docker"],
        resources=[
            Resource(id="r26", title="DB Connection Pooling in Practice", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),

    # --- API design ---
    SkillNode(
        id="api_versioning",
        name="API Versioning",
        category="web",
        difficulty_tier=2,
        prerequisites=["rest_apis"],
        resources=[
            Resource(id="r27", title="Strategies for API Versioning", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),
    SkillNode(
        id="graphql_basics",
        name="GraphQL Basics",
        category="web",
        difficulty_tier=3,
        prerequisites=["rest_apis"],
        resources=[
            Resource(id="r28", title="Intro to GraphQL", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="rate_limiting",
        name="API Rate Limiting",
        category="web",
        difficulty_tier=3,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r29", title="Rate Limiting Patterns", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),

    # --- Security ---
    SkillNode(
        id="input_validation",
        name="Input Validation & Sanitization",
        category="security",
        difficulty_tier=2,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r30", title="Validating User Input Safely", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="cors_deep_dive",
        name="CORS Deep Dive",
        category="security",
        difficulty_tier=2,
        prerequisites=["http_basics"],
        resources=[
            Resource(id="r31", title="Understanding CORS", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),
    SkillNode(
        id="secrets_management",
        name="Secrets Management",
        category="security",
        difficulty_tier=3,
        prerequisites=["docker"],
        resources=[
            Resource(id="r32", title="Managing Secrets in Production", type=ResourceType.COURSE, est_hours=4),
        ],
    ),
    SkillNode(
        id="sql_injection_prevention",
        name="SQL Injection Prevention",
        category="security",
        difficulty_tier=2,
        prerequisites=["sql_basics", "input_validation"],
        resources=[
            Resource(id="r33", title="Preventing SQL Injection", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),

    # --- System design ---
    SkillNode(
        id="cap_theorem",
        name="CAP Theorem",
        category="architecture",
        difficulty_tier=3,
        prerequisites=["system_design_basics"],
        resources=[
            Resource(id="r34", title="CAP Theorem Explained", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),
    SkillNode(
        id="database_sharding",
        name="Database Sharding",
        category="architecture",
        difficulty_tier=4,
        prerequisites=["cap_theorem", "query_optimization"],
        resources=[
            Resource(id="r35", title="Sharding Strategies at Scale", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="event_driven_architecture",
        name="Event-Driven Architecture",
        category="architecture",
        difficulty_tier=4,
        prerequisites=["message_queues"],
        resources=[
            Resource(id="r36", title="Designing Event-Driven Systems", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="api_gateways",
        name="API Gateways",
        category="architecture",
        difficulty_tier=3,
        prerequisites=["rest_apis", "auth"],
        resources=[
            Resource(id="r37", title="API Gateway Patterns", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="circuit_breakers",
        name="Circuit Breakers",
        category="architecture",
        difficulty_tier=4,
        prerequisites=["system_design_basics", "rate_limiting"],
        resources=[
            Resource(id="r38", title="Resilience with Circuit Breakers", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),

    # --- Observability ---
    SkillNode(
        id="logging_best_practices",
        name="Logging Best Practices",
        category="observability",
        difficulty_tier=2,
        prerequisites=["fastapi"],
        resources=[
            Resource(id="r39", title="Structured Logging for APIs", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),
    SkillNode(
        id="monitoring_alerting",
        name="Monitoring & Alerting",
        category="observability",
        difficulty_tier=3,
        prerequisites=["logging_best_practices", "docker"],
        resources=[
            Resource(id="r40", title="Monitoring Production Systems", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="distributed_tracing",
        name="Distributed Tracing",
        category="observability",
        difficulty_tier=4,
        prerequisites=["monitoring_alerting", "message_queues"],
        resources=[
            Resource(id="r41", title="Tracing Requests Across Services", type=ResourceType.COURSE, est_hours=6),
        ],
    ),
    SkillNode(
        id="health_checks",
        name="Health Checks",
        category="observability",
        difficulty_tier=2,
        prerequisites=["fastapi", "docker"],
        resources=[
            Resource(id="r42", title="Designing Health Check Endpoints", type=ResourceType.ARTICLE, est_hours=2),
        ],
    ),

    # --- Testing ---
    SkillNode(
        id="integration_testing",
        name="Integration Testing",
        category="quality",
        difficulty_tier=3,
        prerequisites=["testing", "orm"],
        resources=[
            Resource(id="r43", title="Integration Testing FastAPI + DB", type=ResourceType.COURSE, est_hours=5),
        ],
    ),
    SkillNode(
        id="load_testing",
        name="Load Testing",
        category="quality",
        difficulty_tier=3,
        prerequisites=["testing", "scalability"],
        resources=[
            Resource(id="r44", title="Load Testing with Locust", type=ResourceType.COURSE, est_hours=5),
        ],
    ),

    # --- DevOps ---
    SkillNode(
        id="infra_as_code",
        name="Infrastructure as Code (Terraform)",
        category="devops",
        difficulty_tier=3,
        prerequisites=["cloud_deployment"],
        resources=[
            Resource(id="r45", title="Terraform Fundamentals", type=ResourceType.COURSE, est_hours=8),
        ],
    ),
    SkillNode(
        id="blue_green_deployment",
        name="Blue-Green Deployment",
        category="devops",
        difficulty_tier=4,
        prerequisites=["cloud_deployment", "ci_cd"],
        resources=[
            Resource(id="r46", title="Zero-Downtime Deployment Strategies", type=ResourceType.ARTICLE, est_hours=3),
        ],
    ),
    SkillNode(
        id="kubernetes_basics",
        name="Kubernetes Basics",
        category="devops",
        difficulty_tier=4,
        prerequisites=["docker", "cloud_deployment"],
        resources=[
            Resource(id="r47", title="Kubernetes for Backend Developers", type=ResourceType.COURSE, est_hours=10),
        ],
    ),
]