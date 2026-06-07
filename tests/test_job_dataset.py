import csv
from pathlib import Path


def test_job_seed_dataset_exists_with_target_volume() -> None:
    dataset_path = Path("seed_data/jobs.csv")

    assert dataset_path.exists()

    with dataset_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert 500 <= len(rows) <= 5000


def test_job_seed_dataset_has_import_columns() -> None:
    dataset_path = Path("seed_data/jobs.csv")

    with dataset_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        assert reader.fieldnames == [
            "title",
            "company",
            "location",
            "remote_ok",
            "visa_sponsorship",
            "min_salary",
            "max_salary",
            "required_skills",
            "description",
        ]
