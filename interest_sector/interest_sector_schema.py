from pydantic import BaseModel
from datetime import datetime

class InterestSectorRequest(BaseModel):
    sectorKey: str

class InterestSectorResponse(BaseModel):
    sectorKey: str
    sectorDisplay: str
    registeredAt: datetime
