from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db.database import init_db

app = FastAPI(
    title="AI-Powered Personalized Learning Path Recommender",
    description="HCLTech AMPLified AI Challenge — build track",
    version="0.1.0",
)

# Wide-open CORS for hackathon speed — tighten before the deployed URL goes
# into the submission if you want to be careful about it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "learning-path-recommender"}

@app.on_event("startup")
def on_startup() -> None:
    # Creates tables if they don't exist yet (Base.metadata.create_all).
    # Hackathon-speed choice: no Alembic migrations here. If this goes to
    # production, replace this with versioned Alembic migrations instead
    # of inferring schema from the models at boot time.
    init_db()
