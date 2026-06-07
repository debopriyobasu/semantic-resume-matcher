from src.core.prompts import load_prompt, render_prompt


def test_prompt_files_load_successfully() -> None:
    assert "Resume text:" in load_prompt("resume_extraction.md")
    assert "Candidate:" in load_prompt("matchmaker.md")
    assert "Skills Alignment" in load_prompt("evaluation_criteria.md")


def test_prompt_renderer_substitutes_expected_values() -> None:
    rendered = render_prompt(
        "matchmaker.md",
        {
            "candidate_profile": "Python developer with FastAPI experience",
            "job_posting": "Backend Engineer role requiring Python",
            "evaluation_criteria": "Prioritize backend API experience",
        },
    )

    assert "Python developer with FastAPI experience" in rendered
    assert "Backend Engineer role requiring Python" in rendered
    assert "Prioritize backend API experience" in rendered
