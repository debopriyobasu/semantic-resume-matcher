import logging
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.core.metrics import metrics_store
from src.db.session import get_db
from src.repositories.candidate_repository import create_candidate
from src.schemas.upload import UploadResumeResponse
from src.services.pipeline_service import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"application/pdf"}


@router.post("/upload-resume", response_model=UploadResumeResponse, status_code=200)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    desired_salary: int | None = Form(None),
    visa_required: bool | None = Form(None),
    preferred_location: str | None = Form(None),
    preferred_remote: bool | None = Form(None),
    db: Session = Depends(get_db),
) -> UploadResumeResponse:
    """
    Upload a candidate's resume (PDF format) along with optional filtering criteria.

    Launches an asynchronous background pipeline that:
    1. Parses the PDF resume content using local LLM extraction.
    2. Stores the candidate profile and preferences in the database.
    3. Generates high-density vector embeddings of the profile.
    4. Evaluates the candidate against all active job postings to generate semantic matches.

    **Note:** Only PDF files up to 10MB are supported.
    """
    logger.info("Upload request received")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if file.filename and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    magic_bytes = await file.read(5)
    if magic_bytes != b"%PDF-":
        raise HTTPException(status_code=400, detail="Invalid PDF file format")

    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    await file.seek(0)

    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}.pdf"
    resume_path = os.path.join(uploads_dir, unique_filename)

    with open(resume_path, "wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)

    original_filename = file.filename or "unknown.pdf"
    candidate = create_candidate(
        db,
        resume_path=resume_path,
        original_filename=original_filename,
        desired_salary=desired_salary,
        visa_required=visa_required,
        preferred_location=preferred_location,
        preferred_remote=preferred_remote,
    )

    metrics_store.increment_pipeline_status("PENDING")

    background_tasks.add_task(run_pipeline, candidate.candidate_id)

    return UploadResumeResponse(
        candidate_id=candidate.candidate_id, status=candidate.pipeline_status
    )
