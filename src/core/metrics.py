from threading import Lock
from typing import Dict, List, Any

class MetricsStore:
    """In-memory thread-safe metrics store."""
    def __init__(self) -> None:
        self._lock = Lock()
        
        # Durations
        self._pipeline_durations: List[float] = []
        self._embedding_durations: List[float] = []
        
        # Distributions & Counts
        self._match_confidence_distribution: Dict[str, int] = {
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }
        
        self._pipeline_status_counts: Dict[str, int] = {
            "COMPLETE": 0,
            "FAILED": 0,
            "PENDING": 0
        }
        
        self._match_category_counts: Dict[str, int] = {
            "STRONG_MATCH": 0,
            "POTENTIAL_MATCH": 0,
            "WEAK_MATCH": 0,
            "REJECTED": 0
        }

    def record_pipeline_duration(self, duration_seconds: float) -> None:
        with self._lock:
            self._pipeline_durations.append(duration_seconds)
            
    def record_embedding_duration(self, duration_seconds: float) -> None:
        with self._lock:
            self._embedding_durations.append(duration_seconds)
            
    def record_match_confidence(self, confidence: float) -> None:
        if confidence is None:
            return
            
        bucket = ""
        if 0.0 <= confidence <= 0.2:
            bucket = "0.0-0.2"
        elif 0.2 < confidence <= 0.4:
            bucket = "0.2-0.4"
        elif 0.4 < confidence <= 0.6:
            bucket = "0.4-0.6"
        elif 0.6 < confidence <= 0.8:
            bucket = "0.6-0.8"
        elif 0.8 < confidence <= 1.0:
            bucket = "0.8-1.0"
            
        if bucket:
            with self._lock:
                self._match_confidence_distribution[bucket] += 1
                
    def increment_pipeline_status(self, status: str) -> None:
        with self._lock:
            if status in self._pipeline_status_counts:
                self._pipeline_status_counts[status] += 1
            else:
                self._pipeline_status_counts[status] = 1

    def increment_match_category(self, category: str) -> None:
        with self._lock:
            if category in self._match_category_counts:
                self._match_category_counts[category] += 1
            else:
                self._match_category_counts[category] = 1

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            def summarize_durations(durations: List[float]) -> Dict[str, float]:
                count = len(durations)
                if count == 0:
                    return {"count": 0, "average_seconds": 0.0, "total_seconds": 0.0}
                total = sum(durations)
                return {
                    "count": count,
                    "average_seconds": round(total / count, 4),
                    "total_seconds": round(total, 4)
                }

            return {
                "pipeline_duration_seconds": summarize_durations(self._pipeline_durations),
                "embedding_duration_seconds": summarize_durations(self._embedding_durations),
                "match_confidence_distribution": dict(self._match_confidence_distribution),
                "pipeline_status_counts": dict(self._pipeline_status_counts),
                "match_category_counts": dict(self._match_category_counts)
            }

# Global singleton metrics store
metrics_store = MetricsStore()
