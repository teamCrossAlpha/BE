from fastapi import APIRouter, Depends

from common.dependencies import get_current_user_id
from rag.rag_schema import (
    ChartAssistantRequest,
    ChartAssistantResponse,
)
from rag.rag_service import ask_chart_assistant

router = APIRouter(
    prefix="/api/tickers",
    tags=["RAG Assistant"],
)


@router.post(
    "/{ticker}/assistant",
    response_model=ChartAssistantResponse,
)
def ask_chart_assistant_route(
    ticker: str,
    req: ChartAssistantRequest,
    user_id: int = Depends(get_current_user_id),
):
    return ask_chart_assistant(
        ticker=ticker,
        question=req.question,
        range_=req.range,
    )