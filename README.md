# Semantic Resume Matcher

AI-powered resume-to-job matching system built with FastAPI, PostgreSQL, pgvector, and Gemini.

Upload a PDF resume, extract structured candidate information using Gemini, perform semantic job matching using vector search, apply deterministic business constraints, and generate explainable job recommendations.

---

## Features

### Resume Understanding

* PDF resume upload
* Resume text extraction
* Structured candidate profile generation using Gemini
* Validation of extracted candidate data

### Semantic Search

* Candidate embeddings using `text-embedding-004`
* Vector similarity search with PostgreSQL + pgvector
* Top-N job retrieval based on semantic relevance

### Match Evaluation

* Hard constraint filtering

  * Visa requirements
  * Location preferences
  * Salary expectations
* Gemini-powered fit analysis
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
Gemini Resume Structuring
      │
      ▼
Candidate Embedding
      │
      ▼
pgvector Similarity Search
      │
      ▼
Constraint Filtering
      │
      ▼
Gemini Match Evaluation
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
| LLM              | Gemini 2.0 Flash   |
| Embeddings       | text-embedding-004 |
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

Here is a quick walkthrough of the core features via `curl`. Ensure the application and database are running and bootstrapped first (`docker compose up` and `make bootstrap`).

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
* Gemini API Key

---

### Environment Variables

Create:

```bash
cp .env.example .env
```

Populate:

```env
DATABASE_URL=postgresql://...
GOOGLE_API_KEY=...
```

---

### Start Application

```bash
docker compose up
```

---

### Bootstrap Data

```bash
make bootstrap
```

This command:

* Runs migrations
* Imports job dataset
* Generates job embeddings

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

## Design Decisions

### Why PostgreSQL + pgvector Instead of Pinecone?

For a portfolio project:

* Simpler local setup
* No external vector database account
* Easier GitHub reproducibility
* Lower operational complexity

---

### Why Modular Monolith Instead of Microservices?

The project focuses on:

* AI workflows
* Vector search
* Backend engineering

A modular monolith provides:

* Faster development
* Easier debugging
* Lower infrastructure overhead

while preserving clear module boundaries.

---

### Why Gemini Only For Extraction and Evaluation?

Gemini is intentionally limited to:

* Resume extraction
* Match evaluation

Deterministic code handles:

* Validation
* Filtering
* Similarity search
* Business rules

This improves reliability and reduces cost.

---

## Future Enhancements

* Match history dashboard
* Candidate feedback loop
* Multi-language resume support
* Job scraping integrations
* Scheduled re-matching
* Explainable match highlighting

---

## License

MIT License
