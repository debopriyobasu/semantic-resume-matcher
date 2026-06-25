# Semantic Resume Matcher (Offline)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Offline--LLM-black?style=flat-square)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

An enterprise-grade, **completely local and offline** resume-to-job matching system. Built using **FastAPI, PostgreSQL, pgvector, and Ollama**, this application automates the recruitment pipeline—parsing resumes, searching semantically, and running fit assessments—whilst guaranteeing absolute data privacy by executing entirely on your local machine.

---

## Business Value

Modern candidate screening pipelines face major operational hurdles:

1. **PII Data Privacy & GDPR/CCPA Compliance**: Resumes contain sensitive Personally Identifiable Information (PII). Sending candidate profiles to external cloud LLM APIs poses severe legal, security, and compliance risks. *This system processes all data locally on your infrastructure.*
2. **Exorbitant API Costs**: Running cloud-based LLM parsing and evaluation across thousands of resumes becomes cost-prohibitive. *This solution runs local, open-source models (like Gemma 3 and Llama 3.2 via Ollama) at zero incremental inference cost.*
3. **Keyword-Search Limits**: Classical Applicant Tracking Systems (ATS) miss qualified candidates if they use synonyms or different phrasing. *Our vector search handles semantic concepts rather than plain keywords.*
4. **Unconstrained AI Hallucinations**: Standard LLM screeners may recommend candidates who do not meet hard organizational constraints (e.g., visa sponsorship, location, or salary expectations). *Our hybrid engine combines mathematical vector search with deterministic business rules and LLM reasoning.*

---

## Core Capabilities

### 1. Structured Candidate Profile Extraction
* **Document Text Extraction**: Seamlessly extracts raw text from PDF resume uploads using PyPDF.
* **Schema-Constrained LLM Parsing**: Transforms unstructured resume text into a structured, validated JSON format (detailing core skills, work history, and education) using local LLMs.
* **Pydantic Validation**: Guarantees data integrity before insertion into database records.

### 2. Hybrid Semantic Vector Search
* **Local Embedding Generation**: Encodes candidate profiles and job descriptions into high-density vector representations using `nomic-embed-text` locally.
* **Relational Vector Search**: Performs cosine similarity search directly inside PostgreSQL using the `pgvector` extension to instantly locate candidates whose profiles align with available job postings.

### 3. Deterministic Recruiter Guardrails
* Automatically applies hard business constraints to ensure zero compliance mismatches:
  * **Visa Requirements**: Filters jobs based on candidates' sponsorship needs and the role's eligibility.
  * **Salary Expectations**: Assesses candidate salary thresholds against job salary bounds.
  * **Location & Remote Prefs**: Matches physical location and remote-only preferences.

### 4. Explainable Fit Analysis
* **Natural Language Reasoning**: Generates clean, human-readable explanations of why a candidate fits a role, avoiding black-box decisions.
* **Standout Strengths**: Automatically highlights candidate qualifications that align perfectly with the role.
* **Skill Gap Identification**: Detects missing requirements to help recruiters prepare for follow-up screening interviews.

---

## System Architecture

Our multi-stage pipeline combines the raw speed of database-level vector indexing with the qualitative reasoning of local LLMs. The local system boundary isolates all PII and processing, executing entirely on your local machine:

![System Architecture](docs/architecture.svg)

> [!TIP]
> **Interactive Diagram**: The system architecture diagram is available as an offline-editable Draw.io document. You can open and edit [docs/architecture.drawio](docs/architecture.drawio) using the desktop app, [draw.io web app](https://app.diagrams.net/), or the VS Code Draw.io extension.


---

## Technology Stack & Engineering Design

* **FastAPI**: Asynchronous Python API gateway utilizing Dependency Injection, middleware context tracing, and automatic interactive API documentation.
* **PostgreSQL + pgvector**: A robust, standard database setup that integrates vector similarity search without introducing complex, external vector DB dependencies.
* **Clean Database Design**: Separate entities for business models (`Candidate`, `JobPosting`) and embeddings (`CandidateEmbedding`, `JobEmbedding`). This design:
  * Keeps core database tables clean and lightweight.
  * Treats embeddings as derived data, enabling simple bulk re-embedding or upgrade of LLM models without affecting business data.
* **Database Migrations**: Fully managed database schema evolution using **Alembic** migrations.
* **Enterprise Observability**: Custom JSON structured logging setup linked with request trace-ID propagation middleware to track calls end-to-end.
* **Testing Excellence**: Comprehensive test suites (unit, integration, and golden dataset regression tests) asserting pipeline accuracy and stability.

### Technical Stack Details

| Layer | Technology | Rationale & Rationale Details |
| :--- | :--- | :--- |
| **API Framework** | FastAPI | Asynchronous performance, request/response validation using Pydantic, and automatic Swagger UI. |
| **Database** | PostgreSQL 15 | Time-tested relational database ensuring transactional ACID guarantees. |
| **Vector Indexing** | pgvector | Cosine similarity vector search directly inside SQL queries. |
| **ORM** | SQLAlchemy 2.0 | Type-safe Object Relational Mapper with async database session management. |
| **Migrations** | Alembic | Version-controlled, reproducible database schema migrations. |
| **LLMs / Embedding** | Ollama | Local inference server managing `gemma3:1b` (or `llama3.2`) and `nomic-embed-text`. |
| **PDF Parsing** | PyPDF | Lightweight, dependency-free text extraction from uploaded PDFs. |
| **Containerization** | Docker Compose | One-command local development setup mirroring staging configurations. |

---

## Project Structure

The project directory follows a domain-driven architectural layout designed for maintainability and scalability:

```text
semantic-resume-matcher/
├── src/
│   ├── api/             # HTTP Controllers, routers, and request tracking middleware
│   ├── core/            # App configuration (Pydantic Settings), logger setup, and globals
│   ├── db/              # Database session engine and base models
│   ├── models/          # SQLAlchemy Database entities (Candidate, Job, Match)
│   ├── repositories/    # Clean Data Access Object (DAO) layer decoupling database logic
│   ├── schemas/         # Pydantic validation schemas for API inputs/outputs
│   └── services/        # Core orchestrators: PDF parsers, LLM prompts, & vector matches
├── prompts/             # Modular system instructions (resume parser, matchmaker criteria)
├── scripts/             # Data bootstrapping, CSV importers, and batch embedders
├── tests/               # Pytest directories (unit, integration, and golden dataset regressions)
├── seed_data/           # Sample jobs CSV data & resume mock files
├── uploads/             # Volatile directory for processing PDF uploads
└── migrations/          # Versioned Alembic migrations scripts
```

---

## API Endpoints

Once running, the application serves several REST endpoints to facilitate the matching lifecycle. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

### 1. Health Check
Checks backend and database connectivity.
* **Endpoint**: `GET /health`
* **Response**:
  ```json
  {
    "status": "healthy",
    "database": "connected"
  }
  ```

### 2. Upload Resume
Submit a PDF resume along with explicit candidate preferences.
* **Endpoint**: `POST /upload-resume`
* **Form-Data Params**:
  * `file`: (Binary PDF File)
  * `desired_salary`: `120000` (Optional)
  * `visa_required`: `false` (Optional)
  * `preferred_location`: `San Francisco, CA` (Optional)
  * `preferred_remote`: `true` (Optional)
* **Response**:
  ```json
  {
    "candidate_id": "8f3a6b2c-7d9e-4f1a-b3c5-9d8e7f6a5b4c",
    "status": "PENDING"
  }
  ```

### 3. Check Candidate Parsing Status
Poll the background extraction state for the candidate.
* **Endpoint**: `GET /candidate/{candidate_id}`
* **Response**:
  ```json
  {
    "candidate_id": "8f3a6b2c-7d9e-4f1a-b3c5-9d8e7f6a5b4c",
    "status": "COMPLETE",
    "profile": {
      "full_name": "Jane Doe",
      "email": "jane.doe@example.com",
      "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
      "experience_years": 4
    }
  }
  ```

### 4. Fetch Ranked Matches
Retrieves all matching job positions sorted by semantic similarity, augmented with deterministic constraint status and qualitative match reasoning.
* **Endpoint**: `GET /candidate/{candidate_id}/matches`
* **Response**:
  ```json
  {
    "candidate_id": "8f3a6b2c-7d9e-4f1a-b3c5-9d8e7f6a5b4c",
    "status": "COMPLETE",
    "matches": [
      {
        "job_id": "4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e",
        "title": "Backend Software Engineer",
        "company": "Northstar Labs",
        "vector_score": 0.91,
        "confidence": 0.87,
        "match_category": "STRONG_MATCH",
        "reasoning": "Jane's strong background in Python and async FastAPI matches the core stack requirements. She fits the salary bounds and does not require sponsorship.",
        "skill_gaps": ["Kubernetes"],
        "standout_strengths": ["4+ years writing asynchronous APIs", "Robust Postgres experience"]
      }
    ]
  }
  ```

### 5. System Metrics
Exposes key platform indicators (useful for monitoring dashboard integration).
* **Endpoint**: `GET /metrics`

### 6. Upload Jobs Dataset
Upload or replace the job listings database with a CSV file. Spawns an asynchronous background task to automatically generate vector embeddings for new or updated jobs.
* **Endpoint**: `POST /jobs/upload`
* **Query Params**:
  * `mode`: `update` (default, adds new/updates existing job profiles) or `replace` (deletes all current jobs and loads fresh)
* **Form-Data Params**:
  * `file`: (Binary CSV File)
* **Response**:
  ```json
  {
    "status": "success",
    "mode": "update",
    "added_count": 2,
    "updated_count": 1,
    "deleted_count": 0,
    "embedding_completed": false
  }
  ```

### 7. Get Jobs Embedding Status
Retrieve the status of the background embedding job generator.
* **Endpoint**: `GET /jobs/embedding-status`
* **Response**:
  ```json
  {
    "embedding_completed": false,
    "total_jobs": 15,
    "jobs_without_embeddings": 3
  }
  ```

### 8. Delete Jobs Dataset
Delete all job listings and their associated vector embeddings from the database. Due to cascade deletes, matching candidates are also updated accordingly.
* **Endpoint**: `DELETE /jobs`
* **Response**:
  ```json
  {
    "status": "success",
    "message": "Dataset deleted successfully.",
    "deleted_count": 15
  }
  ```

---

## Local Development & Installation

### Prerequisites
* [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
* [Ollama](https://ollama.com/) running locally on the host machine.

### Model Setup
Pull the required local models before starting the application:
```bash
ollama pull gemma3:1b            # Recommended local LLM (or llama3.2)
ollama pull nomic-embed-text    # Required embedding model
```

### Environment Configuration
1. Clone this repository and copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Verify the configuration values in `.env`:
   ```env
   DATABASE_URL=postgresql+psycopg://resume_matcher:resume_matcher@postgres:5432/resume_matcher
   USE_OLLAMA=true
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   OLLAMA_LLM_MODEL=gemma3:1b
   OLLAMA_EMBED_MODEL=nomic-embed-text
   ```

### Start the Platform
Boot the database and FastAPI server using Docker Compose:
```bash
docker compose up -d
```

### Stop the Platform (Retaining Data)
To stop the application containers without deleting the database or losing your saved candidate profiles and job embeddings:
```bash
docker compose down
```

> [!IMPORTANT]
> Standard `docker compose down` preserves the local named volume (`postgres_data`). All your seed data, resumes, matches, and vector embeddings will be retained and automatically loaded the next time you run `docker compose up -d`.
>
> Avoid using the `-v` or `--volumes` flag (e.g., `docker compose down -v`), as that will delete the named volume and permanently destroy all database content.

### Database Seeding & Bootstrapping
Run migrations, seed the database with available job postings, and compute job vector embeddings using a single command:

* **If running Python on your host system:**
  ```bash
  python scripts/bootstrap.py
  ```
* **If running through Docker containers:**
  ```bash
  docker compose exec api python scripts/bootstrap.py
  ```

This bootstrap script:
1. Executes database migrations via Alembic.
2. Imports the job catalog from `seed_data/jobs.csv`.
3. Auto-generates vector embeddings for all job descriptions using Ollama.

---

## Managing the Job Dataset

### Job Dataset Format
The application expects job listings to be seeded from a CSV file located at `seed_data/jobs.csv`. The CSV requires the following columns:
* **`title`**: Job title (string, e.g., `Associate Backend Engineer`)
* **`company`**: Company name (string, e.g., `Northstar Labs`)
* **`location`**: Job location (string, e.g., `San Francisco, CA` or empty)
* **`remote_ok`**: Remote work status (boolean, e.g., `true`, `false`, `1`, `0`, `yes`, `no`)
* **`visa_sponsorship`**: Visa sponsorship status (boolean, e.g., `true`, `false`, `1`, `0`, `yes`, `no`)
* **`min_salary`**: Minimum salary (integer, optional/nullable)
* **`max_salary`**: Maximum salary (integer, optional/nullable)
* **`required_skills`**: Required skills separated by semicolons (string, e.g., `Python;FastAPI;SQLAlchemy;PostgreSQL`)
* **`description`**: Full text description of the job (string)

### Resetting the Dataset & Starting Afresh

You can manage the jobs dataset either through the **REST API endpoints** (recommended) or using **direct database/CLI commands**.

#### Option A: Via the REST API (Recommended)

1. **Delete All Jobs**:
   Send a `DELETE` request to `/jobs`:
   ```bash
   curl -X DELETE http://localhost:8000/jobs
   ```
2. **Upload & Re-Embed a New CSV**:
   Send a `POST` request to `/jobs/upload` with your CSV file. Use `mode=replace` to overwrite the current dataset or `mode=update` to merge new/modified postings:
   ```bash
   curl -X POST "http://localhost:8000/jobs/upload?mode=replace" \
     -F "file=@seed_data/jobs.csv"
   ```
3. **Monitor Embedding Progress**:
   Check the embedding status to ensure background vector generation has completed:
   ```bash
   curl http://localhost:8000/jobs/embedding-status
   ```

#### Option B: Via Database & CLI Commands

Due to PostgreSQL database cascade delete rules, deleting a job posting from `job_postings` will automatically clean up all associated embeddings in `job_embeddings` and matches in `match_results`.

1. **Delete Existing Jobs**
   * If running through Docker:
     ```bash
     docker compose exec postgres psql -U resume_matcher -d resume_matcher -c "TRUNCATE TABLE job_postings CASCADE;"
     ```
   * If running Postgres locally:
     ```bash
     psql "postgresql://resume_matcher:resume_matcher@localhost:5432/resume_matcher" -c "TRUNCATE TABLE job_postings CASCADE;"
     ```

2. **Import and Re-Embed New Data**
   After replacing or editing your `seed_data/jobs.csv`:
   ```bash
   # Import the jobs
   python scripts/import_jobs.py
   
   # Re-generate embeddings for the new jobs
   python scripts/embed_jobs.py
   ```

---

## Running Tests

A robust test suite validates application logic, schema structures, and data matching fidelity.

### Run Unit Tests
```bash
pytest tests/unit
```

### Run Integration Tests
```bash
pytest tests/integration
```

### Run All Tests
```bash
pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
