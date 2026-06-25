# Semantic Resume Matcher (Offline-First)

AI-powered resume-to-job matching system built with FastAPI, PostgreSQL, pgvector, and Ollama.

This application is designed to be **entirely local and offline-first**, running all language models and embedding generation locally on your machine without relying on external cloud APIs.

Upload a PDF resume, extract structured candidate information using local Ollama models, perform semantic job matching using vector search, apply deterministic business constraints, and generate explainable job recommendations.

---

## Features

### Resume Understanding

* PDF resume upload
* Resume text extraction
* Structured candidate profile generation using Ollama (`gemma3:1b` / `llama3.2`)
* Validation of extracted candidate data

### Semantic Search

* Candidate embeddings using local Ollama (`nomic-embed-text`)
* Vector similarity search with PostgreSQL + pgvector
* Top-N job retrieval based on semantic relevance

### Match Evaluation

* Hard constraint filtering

  * Visa requirements
  * Location preferences
  * Salary expectations
* Ollama-powered local fit analysis
* Skill gap detection
* Match confidence scoring

### Engineering Features

* FastAPI REST API
* PostgreSQL 15
* pgvector
* SQLAlchemy 2.0
* Alembic migrations
* Docker Compose
* Structured logging
* Unit and integration testing

---

## Architecture

```text
Resume Upload
      │
      ▼
PDF Extraction
      │
      ▼
Ollama Resume Structuring
      │
      ▼
Ollama Candidate Embedding
      │
      ▼
pgvector Similarity Search
      │
      ▼
Constraint Filtering
      │
      ▼
Ollama Match Evaluation
      │
      ▼
Ranked Match Results
```

---

## Technology Stack

| Layer            | Technology         |
| ---------------- | ------------------ |
| API              | FastAPI            |
| Database         | PostgreSQL 15      |
| Vector Search    | pgvector           |
| ORM              | SQLAlchemy 2.0     |
| Migrations       | Alembic            |
| LLM              | Ollama (gemma3:1b / llama3.2) |
| Embeddings       | Ollama (nomic-embed-text) |
| PDF Parsing      | PyPDF              |
| Testing          | pytest             |
| Containerization | Docker Compose     |

---

## Project Structure

```text
semantic-resume-matcher/

├── src/
│   ├── api/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── db/
│   └── core/

├── prompts/
│   ├── resume_extraction.md
│   ├── matchmaker.md
│   └── evaluation_criteria.md

├── scripts/
│   ├── import_jobs.py
│   ├── embed_jobs.py
│   └── bootstrap.py

├── tests/
│   ├── unit/
│   ├── integration/
│   └── golden/

├── seed_data/
├── uploads/
└── migrations/
```

---

## Data Model

### Core Entities

```text
Candidate
CandidateEmbedding

JobPosting
JobEmbedding

MatchResult
```

### Design Decision

Embeddings are stored separately from business entities.

Benefits:

* Keeps source data clean
* Treats embeddings as derived data
* Supports future re-embedding
* Simplifies model upgrades

---

## API Endpoints

### Health Check

```http
GET /health
```

---

### Upload Resume

```http
POST /upload-resume
```

Returns:

```json
{
  "candidate_id": "uuid",
  "status": "PENDING"
}
```

---

### Candidate Status

```http
GET /candidate/{candidate_id}
```

---

### Match Results

```http
GET /candidate/{candidate_id}/matches
```

Returns:

```json
{
  "candidate_id": "uuid",
  "status": "COMPLETE",
  "matches": [
    {
      "job_id": "uuid",
      "vector_score": 0.91,
      "confidence": 0.84,
      "match_category": "STRONG_MATCH",
      "reasoning": "...",
      "skill_gaps": [],
      "standout_strengths": []
    }
  ]
}
```

---

## Demo

Here is a quick walkthrough of the core features via `curl`. Ensure the application and database are running and bootstrapped first (`docker compose up` and the bootstrap script).

### 1. Upload Resume

Upload a PDF resume with optional candidate preferences:

```bash
curl -X POST "http://localhost:8000/upload-resume" \
  -F "file=@resume.pdf" \
  -F "desired_salary=120000" \
  -F "visa_required=false" \
  -F "preferred_location=San Francisco, CA" \
  -F "preferred_remote=true"
```

*Save the returned `candidate_id` for the next steps.*

### 2. Candidate Status

Check if the resume extraction and evaluation process is complete:

```bash
curl -X GET "http://localhost:8000/candidate/{candidate_id}"
```

### 3. Match Results

Once the candidate status is `COMPLETE`, fetch the top job matches (this may take a few seconds if evaluating dynamically):

```bash
curl -X GET "http://localhost:8000/candidate/{candidate_id}/matches"
```

### 4. Metrics Endpoint

View system-level metrics, such as total candidates processed and match statistics:

```bash
curl -X GET "http://localhost:8000/metrics"
```

---

## Local Development

### Prerequisites

* Docker
* Docker Compose
* [Ollama](https://ollama.com/) running on your host machine

Ensure you have pulled the required local models before starting the application:
```bash
ollama pull gemma3:1b            # Recommended local LLM (or llama3.2)
ollama pull nomic-embed-text    # Required embedding model
```

---

### Environment Variables

Create:

```bash
cp .env.example .env
```

Populate:

```env
DATABASE_URL=postgresql+psycopg://resume_matcher:resume_matcher@postgres:5432/resume_matcher
USE_OLLAMA=true
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_LLM_MODEL=gemma3:1b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

---

### Start Application

```bash
docker compose up
```

---

### Bootstrap Data

To run migrations, import job postings, and generate their embeddings in a single cross-platform command:

* **If running locally:**
  ```bash
  python scripts/bootstrap.py
  ```

* **If running through Docker:**
  ```bash
  docker compose exec api python scripts/bootstrap.py
  ```

This script:

* Runs database migrations via Alembic
* Imports the job dataset from `seed_data/jobs.csv`
* Generates job embeddings using Ollama (`nomic-embed-text`)

---

### Managing the Job Dataset

#### Job Dataset Format
The application expects job listings to be seeded from a CSV file located at `seed_data/jobs.csv`. The CSV requires the following columns:
* **`title`**: Job title (string, e.g., `Associate Backend Engineer`)
* **`company`**: Company name (string, e.g., `Northstar Labs`)
* **`location`**: Job location (string, optional/nullable, e.g., `San Francisco, CA` or empty)
* **`remote_ok`**: Remote work status (boolean, e.g., `true`, `false`, `1`, `0`, `yes`, `no`)
* **`visa_sponsorship`**: Visa sponsorship status (boolean, e.g., `true`, `false`, `1`, `0`, `yes`, `no`)
* **`min_salary`**: Minimum salary (integer, optional/nullable)
* **`max_salary`**: Maximum salary (integer, optional/nullable)
* **`required_skills`**: Required skills separated by semicolons (string, e.g., `Python;FastAPI;SQLAlchemy;PostgreSQL`)
* **`description`**: Full text description of the job (string)

#### Resetting the Dataset & Starting Afresh
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

### Open Swagger

```text
http://localhost:8000/docs
```

---

## Running Tests

### Unit Tests

```bash
pytest tests/unit
```

### Integration Tests

```bash
pytest tests/integration
```

### All Tests

```bash
pytest
```

---


## License

MIT License
