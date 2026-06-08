from sqlalchemy.orm import Session

from src.models.candidate import Candidate
from src.schemas.candidate import CandidateProfile


def create_candidate(
    db: Session, 
    resume_path: str, 
    original_filename: str,
    desired_salary: int | None = None,
    visa_required: bool | None = None,
    preferred_location: str | None = None,
    preferred_remote: bool | None = None,
) -> Candidate:
    candidate = Candidate(
        resume_path=resume_path,
        original_filename=original_filename,
        desired_salary=desired_salary,
        visa_required=visa_required,
        preferred_location=preferred_location,
        preferred_remote=preferred_remote,
        pipeline_status="PENDING",
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def update_candidate_profile(db: Session, candidate_id: str, profile: CandidateProfile) -> Candidate | None:
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        return None
        
    if profile.name is not None:
        candidate.name = profile.name
    if profile.email is not None:
        candidate.email = profile.email
    if profile.skills is not None:
        candidate.skills = profile.skills
    if profile.experience_years is not None:
        candidate.experience_years = profile.experience_years
    if profile.education is not None:
        candidate.education = profile.education
    if profile.location is not None:
        candidate.location = profile.location
        
    db.commit()
    db.refresh(candidate)
    return candidate
