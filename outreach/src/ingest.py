"""Ingest PDFs into a local Chroma vector store for retrieval."""

from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets" / "knowledge_base"
CHROMA_DIR = ROOT_DIR / "chroma_db"


def load_pdfs(pdf_dir: Path) -> List:
    """Load all PDFs from the knowledge base directory."""
    pdf_paths = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(
            f"No PDF files found in {pdf_dir}. Add lab papers before running ingestion."
        )
    documents = []
    for pdf_path in pdf_paths:
        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())
    return documents


def split_documents(documents: List, chunk_size: int = 1000, chunk_overlap: int = 100):
    """Split documents into chunks suitable for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)


def build_vectorstore(chunks, persist_dir: Path = CHROMA_DIR):
    """Create a Chroma vector store from chunks and persist it to disk."""
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    vectorstore.persist()
    return vectorstore


def ingest():
    """Orchestrate the PDF loading, splitting, and vectorstore creation."""
    load_dotenv()
    documents = load_pdfs(ASSETS_DIR)
    chunks = split_documents(documents)
    build_vectorstore(chunks)
    print(f"Vector store created at {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()
