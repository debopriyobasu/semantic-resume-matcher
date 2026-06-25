import csv
import io
import logging
from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.job_embedding import JobEmbedding
from src.models.job_posting import JobPosting
from src.repositories.job_repository import delete_all_jobs
from src.schemas.jobs import JobDeleteResponse, JobEmbeddingStatusResponse, JobUploadResponse
from src.services.embedding_service import process_job_embeddings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def parse_optional_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(stripped)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid integer value: '{value}'"
        ) from e


@router.post("/upload", response_model=JobUploadResponse, status_code=status.HTTP_200_OK)
async def upload_jobs(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Query("update", enum=["update", "replace"]),
    db: Session = Depends(get_db),
) -> JobUploadResponse:
    """
    Upload a CSV file containing job listings to the database.

    Supports two modes of operation:
    - **update** (default): Adds new job listings and updates existing ones (based on matching Title and Company).
      If an existing job listing is modified, its corresponding embedding is removed and regenerated.
    - **replace**: Deletes all existing job listings and starts fresh with the uploaded dataset.

    Triggers an asynchronous background task to generate vector embeddings for any newly added or updated job postings.

    **Note:** Only CSV files are allowed. The CSV must contain the following columns:
    `title`, `company`, `location`, `remote_ok`, `visa_sponsorship`, `min_salary`, `max_salary`, `required_skills`, `description`.
    """
    logger.info("Received jobs dataset upload request with mode: %s", mode)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are allowed"
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty")

    try:
        csv_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file encoding must be UTF-8"
        ) from e

    reader = csv.DictReader(io.StringIO(csv_content))
    expected_cols = {
        "title",
        "company",
        "location",
        "remote_ok",
        "visa_sponsorship",
        "min_salary",
        "max_salary",
        "required_skills",
        "description",
    }

    if not reader.fieldnames or not expected_cols.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV must contain headers: {', '.join(expected_cols)}",
        )

    parsed_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(reader, start=1):
        title = row.get("title", "").strip()
        company = row.get("company", "").strip()
        description = row.get("description", "").strip()

        if not title or not company or not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {idx} is invalid: title, company, and description are required and cannot be empty",
            )

        parsed_rows.append(
            {
                "title": title,
                "company": company,
                "location": row.get("location", "").strip() or None,
                "remote_ok": parse_bool(row.get("remote_ok", "")),
                "visa_sponsorship": parse_bool(row.get("visa_sponsorship", "")),
                "min_salary": parse_optional_int(row.get("min_salary", "")),
                "max_salary": parse_optional_int(row.get("max_salary", "")),
                "required_skills": [
                    skill.strip()
                    for skill in row.get("required_skills", "").split(";")
                    if skill.strip()
                ],
                "description": description,
            }
        )

    if not parsed_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file contains no job records"
        )

    added_count = 0
    updated_count = 0
    deleted_count = 0

    import uuid

    if mode == "replace":
        deleted_count = delete_all_jobs(db)
        new_jobs = [JobPosting(job_id=uuid.uuid4(), **row_data) for row_data in parsed_rows]
        db.add_all(new_jobs)
        db.commit()
        added_count = len(new_jobs)
    else:
        # update mode
        existing_jobs = db.scalars(select(JobPosting)).all()
        existing_jobs_dict = {
            (job.title.strip().lower(), job.company.strip().lower()): job for job in existing_jobs
        }

        for row_data in parsed_rows:
            key = (row_data["title"].strip().lower(), row_data["company"].strip().lower())
            if key in existing_jobs_dict:
                existing_job = existing_jobs_dict[key]
                changed = False

                if existing_job.location != row_data["location"]:
                    existing_job.location = row_data["location"]
                    changed = True
                if existing_job.remote_ok != row_data["remote_ok"]:
                    existing_job.remote_ok = row_data["remote_ok"]
                    changed = True
                if existing_job.visa_sponsorship != row_data["visa_sponsorship"]:
                    existing_job.visa_sponsorship = row_data["visa_sponsorship"]
                    changed = True
                if existing_job.min_salary != row_data["min_salary"]:
                    existing_job.min_salary = row_data["min_salary"]
                    changed = True
                if existing_job.max_salary != row_data["max_salary"]:
                    existing_job.max_salary = row_data["max_salary"]
                    changed = True
                if sorted(existing_job.required_skills) != sorted(row_data["required_skills"]):
                    existing_job.required_skills = row_data["required_skills"]
                    changed = True
                if existing_job.description != row_data["description"]:
                    existing_job.description = row_data["description"]
                    changed = True

                if changed:
                    # Remove existing embedding to trigger regeneration
                    db.query(JobEmbedding).filter(
                        JobEmbedding.job_id == existing_job.job_id
                    ).delete()
                    updated_count += 1
            else:
                new_job = JobPosting(job_id=uuid.uuid4(), **row_data)
                db.add(new_job)
                added_count += 1

        db.commit()

    # Determine embedding status
    stmt = (
        select(func.count(JobPosting.job_id))
        .outerjoin(JobEmbedding)
        .where(JobEmbedding.embedding_id.is_(None))
    )
    jobs_without_emb = db.scalar(stmt) or 0
    embedding_completed = jobs_without_emb == 0

    if jobs_without_emb > 0:
        logger.info("Spawning background task to generate embeddings for %d jobs", jobs_without_emb)
        background_tasks.add_task(process_job_embeddings)

    return JobUploadResponse(
        status="success",
        mode=mode,
        added_count=added_count,
        updated_count=updated_count,
        deleted_count=deleted_count,
        embedding_completed=embedding_completed,
    )


@router.get("/embedding-status", response_model=JobEmbeddingStatusResponse)
def get_embedding_status(db: Session = Depends(get_db)) -> JobEmbeddingStatusResponse:
    """
    Retrieve the current status of job embedding generation.

    Returns the completion status, total number of jobs, and the count of jobs that are currently missing vector embeddings.
    """
    total_jobs = db.scalar(select(func.count(JobPosting.job_id))) or 0
    stmt = (
        select(func.count(JobPosting.job_id))
        .outerjoin(JobEmbedding)
        .where(JobEmbedding.embedding_id.is_(None))
    )
    jobs_without_emb = db.scalar(stmt) or 0

    return JobEmbeddingStatusResponse(
        embedding_completed=(jobs_without_emb == 0),
        total_jobs=total_jobs,
        jobs_without_embeddings=jobs_without_emb,
    )


@router.delete("", response_model=JobDeleteResponse)
def delete_jobs_dataset(db: Session = Depends(get_db)) -> JobDeleteResponse:
    """
    Delete all job postings and associated vector embeddings from the database.

    Clears the entire jobs catalog. Due to cascade deletes, all candidate match results associated with these jobs are also deleted.
    """
    deleted_count = delete_all_jobs(db)
    return JobDeleteResponse(
        status="success",
        message="Dataset deleted successfully.",
        deleted_count=deleted_count,
    )
