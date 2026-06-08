import logging
import uuid
import time
from sqlalchemy.orm import Session

from src.core.metrics import metrics_store
from src.core.logger import candidate_id_ctx_var

from src.models.candidate import Candidate
from src.services.resume_parser import ResumeParserService
from src.services.embedding_service import EmbeddingService
from src.services.search_service import SearchService
from src.services.matchmaker_service import MatchmakerService
from src.repositories.candidate_repository import update_candidate_profile
from src.repositories.candidate_embedding_repository import create_candidate_embedding
from src.db.session import SessionLocal

logger = logging.getLogger(__name__)

class PipelineService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_parser = ResumeParserService()
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService(db)
        self.matchmaker_service = MatchmakerService()

    def process_candidate(self, candidate_id: uuid.UUID) -> None:
        candidate_id_ctx_var.set(str(candidate_id))
        start_time = time.perf_counter()
        
        candidate = self.db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if not candidate:
            logger.error(f"Candidate {candidate_id} not found in pipeline.")
            return

        try:
            self._update_status(candidate, "PARSING")
            logger.info("Starting parsing for candidate resume")
            
            with open(candidate.resume_path, "rb") as f:
                file_content = f.read()

            text = self.resume_parser.extract_text(file_content)
            
            profile = self.resume_parser.extract_profile(text)
            update_candidate_profile(self.db, str(candidate_id), profile)
            
            self._update_status(candidate, "EMBEDDING")
            logger.info("Generating embeddings for candidate profile")
            self.db.refresh(candidate)
            embedding = self.embedding_service.generate_candidate_embedding(candidate)
            create_candidate_embedding(self.db, candidate_id, embedding)
            
            self._update_status(candidate, "SEARCHING")
            logger.info("Searching for similar jobs using pgvector")
            # Searching handles filtering and creates MatchResults
            self.search_service.find_similar_jobs(candidate_id)
            
            self._update_status(candidate, "REASONING")
            logger.info("Reasoning over candidate matches with Gemini")
            self.matchmaker_service.evaluate_matches(self.db, candidate_id)
            
            self._update_status(candidate, "COMPLETE")
            metrics_store.increment_pipeline_status("COMPLETE")
            
        except Exception as e:
            logger.error(f"Pipeline failed for candidate {candidate_id}: {e}", exc_info=True)
            self._update_status(candidate, "FAILED")
            metrics_store.increment_pipeline_status("FAILED")
        finally:
            duration = time.perf_counter() - start_time
            metrics_store.record_pipeline_duration(duration)

    def _update_status(self, candidate: Candidate, status: str) -> None:
        candidate.pipeline_status = status
        self.db.commit()
        self.db.refresh(candidate)

def run_pipeline(candidate_id: uuid.UUID) -> None:
    db = SessionLocal()
    try:
        pipeline = PipelineService(db)
        pipeline.process_candidate(candidate_id)
    finally:
        db.close()
