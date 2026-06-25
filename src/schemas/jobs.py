from pydantic import BaseModel, Field


class JobUploadResponse(BaseModel):
    status: str = Field(..., description="The status of the upload operation (typically 'success')")
    mode: str = Field(..., description="The dataset update mode used: 'update' or 'replace'")
    added_count: int = Field(
        ..., description="The number of new job postings added to the database"
    )
    updated_count: int = Field(
        ..., description="The number of existing job postings updated in the database"
    )
    deleted_count: int = Field(
        ..., description="The number of job postings deleted (applicable in 'replace' mode)"
    )
    embedding_completed: bool = Field(
        ..., description="Whether embedding generation is already complete for the uploaded jobs"
    )


class JobEmbeddingStatusResponse(BaseModel):
    embedding_completed: bool = Field(
        ..., description="True if all job postings have corresponding vector embeddings"
    )
    total_jobs: int = Field(..., description="The total number of job postings in the database")
    jobs_without_embeddings: int = Field(
        ..., description="The number of job postings currently missing vector embeddings"
    )


class JobDeleteResponse(BaseModel):
    status: str = Field(..., description="The status of the delete operation (typically 'success')")
    message: str = Field(
        ..., description="A descriptive message indicating the result of the delete operation"
    )
    deleted_count: int = Field(
        ..., description="The number of job postings deleted from the database"
    )
