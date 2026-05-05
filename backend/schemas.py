# schemas.py
from pydantic import BaseModel, Field

class NotesInput(BaseModel):
    raw_notes: str = Field(..., min_length=5, description="The rough patient notes entered by the staff.")