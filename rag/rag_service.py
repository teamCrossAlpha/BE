from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from tickers.tickers_service import get_technical_summary_with_llm

from common.config import settings

VECTORSTORE_DIR = "rag/vectorstore"


def _load_retriever():
    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_tech_api_key
    )

    vectorstore = FAISS.load_local(
        VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore.as_retriever(search_kwargs={"k": 3})


def _format_docs(docs):
    return "\n\n".join(
        [
            f"[source: {doc.metadata.get('source')}]\n{doc.page_content}"
            for doc in docs
        ]
    )


def _build_snapshot_context(inputs: dict) -> str:
    ticker = inputs["ticker"]
    range_ = inputs.get("range", "3M")

    snapshot = get_technical_summary_with_llm(
        ticker=ticker,
        rng=range_,
    )

    return f"""
ticker: {snapshot.ticker}
range: {snapshot.range}

sma20: {snapshot.indicators.sma20}
sma50: {snapshot.indicators.sma50}
rsi14: {snapshot.indicators.rsi14}

bollinger_upper: {snapshot.indicators.bollinger.upper}
bollinger_middle: {snapshot.indicators.bollinger.middle}
bollinger_lower: {snapshot.indicators.bollinger.lower}

signals: {[s.id for s in snapshot.signals]}
summaryText: {snapshot.summaryText}
""".strip()


def ask_chart_assistant(
    ticker: str,
    question: str,
    range_: str = "3M",
):
    retriever = _load_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
당신은 초보 투자자를 위한 차트 분석 AI 어시스턴트입니다.

규칙:
- 반드시 한국어로 답변합니다.
- 매수/매도 추천은 하지 않습니다.
- 검색된 문서와 현재 기술적 지표만 근거로 답변합니다.
- 차트와 무관한 질문은 제한합니다.
- 답변은 2~4문장으로 작성합니다.
""".strip(),
            ),
            (
                "human",
                """
현재 종목 데이터:
{snapshot_context}

검색된 기술적 분석 문서:
{retrieved_context}

사용자 질문:
{question}
""".strip(),
            ),
        ]
    )

    llm = ChatOpenAI(
        api_key=settings.openai_tech_api_key,
        model="gpt-4o-mini",
        temperature=0.2,
    )

    chain = (
        RunnableParallel(
            {
                "snapshot_context": RunnableLambda(
                    _build_snapshot_context
                ),
                "retrieved_context": (
                    RunnableLambda(lambda x: x["question"])
                    | retriever
                    | RunnableLambda(_format_docs)
                ),
                "question": RunnableLambda(
                    lambda x: x["question"]
                ),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(
        {
            "ticker": ticker,
            "question": question,
            "range": range_,
        }
    )

    return {
        "ticker": ticker.upper(),
        "range": range_,
        "question": question,
        "answer": answer,
    }