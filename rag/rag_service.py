from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisChatMessageHistory

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
    session_id: str = None,
):
    retriever = _load_retriever()

    # 히스토리 로드
    history = RedisChatMessageHistory(
        session_id=session_id,
        redis_url=settings.redis_url,
        ttl=60 * 60 * 24 * 7,  # 7일
    )

    print(history.messages)

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
- 이전 대화 맥락을 기억하고 자연스럽게 이어서 답변합니다.
- 차트 및 기술적 분석과 무관한 질문(종목 추천, 투자 조언 등)은 정중히 거절합니다.
- 답변은 3~5문장으로 작성합니다.
""".strip(),
            ),
            MessagesPlaceholder(variable_name="chat_history"),
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
                "chat_history": RunnableLambda(
                    lambda x: history.messages
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

    # 히스토리 저장
    history.add_user_message(question)
    history.add_ai_message(answer)

    return {
        "ticker": ticker.upper(),
        "range": range_,
        "question": question,
        "answer": answer,
    }