from pydantic import BaseModel
from typing import Optional


class WinRateDTO(BaseModel):
    score: float
    wins: int
    total: int
    ratio: float


class AvgReturnDTO(BaseModel):
    score: float
    averageRate: float


class BadPatternDTO(BaseModel):
    score: float
    badCount: int
    ratio: float


class ConvictionDTO(BaseModel):
    score: float
    rawScore: float
    lowConfidenceWins: int
    message: Optional[str]


class TextBonusDTO(BaseModel):
    score: float
    writeRatio: float


class PerformanceScoreResponse(BaseModel):
    totalScore: float
    winRate: WinRateDTO
    averageReturn: AvgReturnDTO
    badPattern: BadPatternDTO
    conviction: ConvictionDTO
    textBonus: TextBonusDTO