from sqlalchemy.orm import Session
from src.models.candidate import Candidate

def create_candidate(db: Session, resume_path: str, original_filename: str) -> Candidate:
    candidate = Candidate(
        resume_path=resume_path,
        original_filename=original_filename,
        pipeline_status="PENDING",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
