# schemas.py
from pydantic import BaseModel, Field

class NotesInput(BaseModel):
    raw_notes: str = Field(..., description="The rough patient notes entered by the staff.")
