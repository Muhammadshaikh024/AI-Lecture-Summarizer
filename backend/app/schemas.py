from typing import List, Optional
from pydantic import BaseModel


class LectureOut(BaseModel):
    id: int
    filename: str
    raw_text_preview: str

    class Config:
        from_attributes = True


class ProcessOut(BaseModel):
    lecture_id: int
    summary: str
    keywords: List[str]
    questions: List[str]


class LectureDetailOut(BaseModel):
    id: int
    filename: str
    summary: Optional[str] = None
    keywords: List[str] = []
    questions: List[str] = []