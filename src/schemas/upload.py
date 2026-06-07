import uuid
from pydantic import BaseModel

class UploadResumeResponse(BaseModel):
    candidate_id: uuid.UUID
    status: str
