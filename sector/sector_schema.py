from pydantic import BaseModel

class SectorOverviewResponse(BaseModel):
    sectorKey: str
    sectorDisplay: str
    returnRate: float
    isFavorite: bool
