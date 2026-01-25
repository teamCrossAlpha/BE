from pydantic import BaseModel
from datetime import date


class SectorSummaryListResponse(BaseModel):
    id: int
    title: str
    preview: str
    summaryDate: date


class SectorSummaryDetailResponse(BaseModel):
    id: int
    title: str
    preview: str
    content: str
    keyPoints: list[str]
    sources: list[str]
