from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import Feedback, SearchHistory, get_db

router = APIRouter()


@router.get("/api/linkedin/post-data")
def get_linkedin_post_data(db: Session = Depends(get_db)):
    """
    Returns formatted data for writing the next LinkedIn post about Scholr.
    Run this before writing any LinkedIn post to get accurate numbers.
    """
    total = db.query(func.count(SearchHistory.id)).scalar() or 0
    week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = db.query(func.count(SearchHistory.id)).filter(
        SearchHistory.created_at >= week_ago
    ).scalar() or 0

    by_module = db.query(
        SearchHistory.module,
        func.count(SearchHistory.id).label("count")
    ).group_by(SearchHistory.module).order_by(func.count(SearchHistory.id).desc()).all()

    most_used = by_module[0].module if by_module else "research"

    helpful = db.query(func.count(Feedback.id)).filter(
        Feedback.rating == "helpful"
    ).scalar() or 0
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0

    return {
        "post_stats": {
            "total_queries_ever": total,
            "queries_this_week": this_week,
            "most_used_module": most_used,
            "helpful_feedback_count": helpful,
            "total_feedback": total_feedback,
        },
        "suggested_posts": [
            {
                "type": "launch_post",
                "hook": "I built Scholr - a live AI academic platform for BTech students.",
                "body": f"In the last week, students used it {this_week} times.\n\nWhat it does:\n- Research papers + reading order in 60 seconds\n- Exam-ready notes from any topic\n- Step-by-step doubt solving\n\nBuilt with Next.js + FastAPI + Gemini API.\nDeployed on Vercel + Render.\n\nTry it free: https://scholr-coral.vercel.app",
                "cta": "If you are a BTech student or know one - try it and tell me what to improve.",
                "hashtags": "#buildinpublic #btechstudents #AI #edtech #india #nextjs #fastapi #opentowork",
            },
            {
                "type": "progress_post",
                "hook": f"Week update on Scholr - {this_week} AI queries this week.",
                "body": f"Total queries across all modules: {total}\nMost used feature: {most_used.title()}\nFeedback collected: {total_feedback} responses\n\nBiggest learning this week: [add your own insight here]\n\nStill free, still live: https://scholr-coral.vercel.app",
                "cta": "What feature would make this more useful for your BTech work?",
                "hashtags": "#buildinpublic #indiatech #AIstartup #BTech #scholr",
            },
        ],
        "whatsapp_message": "Hey! I built Scholr - an AI tool for BTech students. Type your research topic or exam subject and get structured help in under a minute. Free, no signup needed. Try it: https://scholr-coral.vercel.app - takes 30 seconds to try. Would love your feedback!",
        "generated_at": datetime.utcnow().isoformat(),
    }
