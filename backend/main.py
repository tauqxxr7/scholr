from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from routers import doubt, history, notes, research

init_db()

app = FastAPI(
    title="Scholr API",
    description="AI Academic Platform for BTech Students",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://scholr.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(doubt.router, prefix="/api", tags=["doubt"])
app.include_router(history.router, prefix="/api", tags=["history"])


@app.get("/health")
def health_check():
    return {"status": "Scholr API is running", "version": "1.0.0"}
