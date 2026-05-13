from pydantic import BaseModel


class ChartAssistantRequest(BaseModel):
    question: str
    range: str = "3M"


class ChartAssistantResponse(BaseModel):
    ticker: str
    range: str
    question: str
    answer: str