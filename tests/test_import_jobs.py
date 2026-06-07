from pathlib import Path

from scripts.import_jobs import load_jobs, parse_bool, parse_optional_int


def test_import_script_parses_seed_jobs() -> None:
    jobs = load_jobs(Path("seed_data/jobs.csv"))

    assert jobs
    first_job = jobs[0]
    assert set(first_job) == {
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
    assert isinstance(first_job["remote_ok"], bool)
    assert isinstance(first_job["visa_sponsorship"], bool)
    assert isinstance(first_job["required_skills"], list)


def test_import_script_parses_simple_values() -> None:
    assert parse_bool("true") is True
    assert parse_bool("no") is False
    assert parse_optional_int("125000") == 125000
    assert parse_optional_int("") is None
