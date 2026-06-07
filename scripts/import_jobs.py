from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.db.session import SessionLocal  # noqa: E402
from src.repositories.job_repository import bulk_create_jobs, count_jobs  # noqa: E402

DEFAULT_CSV_PATH = PROJECT_ROOT / "seed_data" / "jobs.csv"


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def parse_optional_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped:
        return None
    return int(stripped)


def load_jobs(csv_path: Path = DEFAULT_CSV_PATH) -> list[dict[str, Any]]:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            {
                "title": row["title"].strip(),
                "company": row["company"].strip(),
                "location": row["location"].strip() or None,
                "remote_ok": parse_bool(row["remote_ok"]),
                "visa_sponsorship": parse_bool(row["visa_sponsorship"]),
                "min_salary": parse_optional_int(row["min_salary"]),
                "max_salary": parse_optional_int(row["max_salary"]),
                "required_skills": [
                    skill.strip()
                    for skill in row["required_skills"].split(";")
                    if skill.strip()
                ],
                "description": row["description"].strip(),
            }
            for row in reader
        ]


def main(csv_path: Path = DEFAULT_CSV_PATH) -> int:
    jobs = load_jobs(csv_path)
    with SessionLocal() as db:
        bulk_create_jobs(db, jobs)
        total_jobs = count_jobs(db)
    print(f"Imported {len(jobs)} jobs from {csv_path}. Database now contains {total_jobs} jobs.")
    return len(jobs)


if __name__ == "__main__":
    main()
