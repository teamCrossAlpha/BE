from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from common.config import settings

DOCS_DIR = Path("rag/docs")
SAVE_DIR = "rag/vectorstore"


def build_vectorstore():
    docs = []

    for path in DOCS_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")

        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": path.name,
                },
            )
        )

    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_tech_api_key
    )

    vectorstore = FAISS.from_documents(
        docs,
        embeddings,
    )

    vectorstore.save_local(SAVE_DIR)

    print(f"saved -> {SAVE_DIR}")


if __name__ == "__main__":
    build_vectorstore()