"""Core RAG pipeline for the Hickey Lab AI Assistant."""

from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


ROOT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = ROOT_DIR / "chroma_db"

SYSTEM_PROMPT = (
    "You are a warm, caring assistant for anyone curious about the Hickey Lab at Duke. "
    "Explain spatial omics and our research in friendly, plain language while staying accurate. "
    "Use the provided context to ground answers; if it is insufficient, gently say you don't have that info yet and invite another question."
)


def load_vectorstore(persist_dir: Path = CHROMA_DIR):
    """Load the persisted Chroma store."""
    if not persist_dir.exists():
        raise FileNotFoundError(
            f"Vector store not found at {persist_dir}. Run src/ingest.py first."
        )
    embeddings = OpenAIEmbeddings()
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
    )


def build_chain():
    """Build the retrieval + generation chain."""
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "system",
                "Use the following context from Hickey Lab publications:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def format_docs(docs: List) -> str:
        return "\n\n".join(doc.page_content for doc in docs)

    chain: RunnableSequence = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
    )
    return chain


def get_response(user_question: str) -> str:
    """Return a model response grounded in the vector store."""
    load_dotenv()
    chain = build_chain()
    response = chain.invoke(user_question)
    return response.content
