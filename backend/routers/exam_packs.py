"""Deterministic, source-aware revision planner. Does not claim AI predictions."""
from collections import Counter
from datetime import date, timedelta
import re

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

router = APIRouter()

class ExamPackRequest(BaseModel):
    subject: str = Field(min_length=2, max_length=120)
    units: list[str] = Field(min_length=1, max_length=12)
    exam_date: date
    previous_year_questions: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("units", "previous_year_questions")
    @classmethod
    def clean_items(cls, items: list[str]) -> list[str]:
        cleaned = [item.strip() for item in items]
        if any(not item or len(item) > 500 for item in cleaned):
            raise ValueError("Each item must contain 1 to 500 characters")
        return cleaned

def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - {
        "the", "and", "for", "with", "from", "what", "explain", "describe",
        "define", "write", "short", "note", "about", "give", "how", "why",
    }

@router.post("/exam-packs/preview")
def preview_exam_pack(payload: ExamPackRequest):
    """Free preview: plan only; no ungrounded question forecasts or paid entitlement."""
    today = date.today()
    days = max(0, (payload.exam_date - today).days)
    units = list(dict.fromkeys(payload.units))
    counts = Counter()
    for question in payload.previous_year_questions:
        qwords = words(question)
        for unit in units:
            tokens = words(unit)
            if tokens and tokens & qwords:
                counts[unit] += 1
    schedule = []
    study_days = min(max(days, 1), 30)
    for i in range(study_days):
        unit = units[i % len(units)]
        schedule.append({
            "date": (today + timedelta(days=i)).isoformat(),
            "unit": unit,
            "task": "Review source notes, practice 2 questions, self-test without notes",
        })
    return {
        "subject": payload.subject.strip(),
        "days_until_exam": days,
        "revision_schedule": schedule,
        "pyq_keyword_matches": [{"unit": unit, "matches": counts[unit]} for unit in units],
        "limitations": [
            "Keyword matches are not a statistical forecast of exam questions.",
            "No syllabus or document grounding has been verified in this preview.",
            "Upload and citation-backed generation require a separate authenticated workflow.",
        ],
        "payment_required": False,
    }
