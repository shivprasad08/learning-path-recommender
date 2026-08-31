"""
Seed skill taxonomy — Backend Development vertical.

This is a starter set (~20 nodes) proving the DAG structure end-to-end.
Before submission, extend this to 40-60 nodes per the plan — add depth in
areas like databases, system design, and deployment rather than breadth
into unrelated domains.

Each node's `prerequisites` list must reference IDs already defined above
it (or anywhere in this file) — the graph builder will raise an error on
cycles or missing references, which is exactly what you want caught early.
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
        prerequisites=["scalability", "message_queues", "cloud_deployment"],
        resources=[
            Resource(id="r20", title="Microservices in Practice", type=ResourceType.COURSE, est_hours=12),
        ],
    ),
]
