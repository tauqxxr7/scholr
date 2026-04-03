from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import research, notes, doubt
from db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scholr API",
    description="AI Academic Platform for BTech Students",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://scholr.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(doubt.router, prefix="/api", tags=["doubt"])

@app.get("/health")
def health_check():
    return {"status": "Scholr API is running", "version": "1.0.0"}
