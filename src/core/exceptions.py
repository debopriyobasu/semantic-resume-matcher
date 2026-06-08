class ResumeParseError(Exception):
    """Exception raised for errors during resume parsing."""
    pass

class EmbeddingError(Exception):
    """Exception raised for errors during embedding generation."""
    pass

class MatchmakingError(Exception):
    """Exception raised for errors during matchmaking."""
    pass

class VectorSearchError(Exception):
    """Exception raised for errors during vector search."""
    pass
