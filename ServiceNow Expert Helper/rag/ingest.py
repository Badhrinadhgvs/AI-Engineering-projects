import os
import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
)
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

## Fixing the constants
KB_PATH = str(Path(__file__).parent.parent / "knowledge-base")
DB = str(Path(__file__).parent.parent / "vector_db")
load_dotenv(override=True)

embedding = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")


def load_documents():
    loader = DirectoryLoader(
        KB_PATH,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print("Documents Loaded Successfully.")
    return [doc for doc in docs]


def make_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)
    return chunks


def encode_chunks(chunks):
    if os.path.exists(DB):
        Chroma(persist_directory=DB, embedding_function=embedding).delete_collection()
    vector_store = Chroma().from_documents(
        documents=chunks, embedding=embedding, persist_directory=DB
    )
    collects = vector_store._collection
    count = collects.count()
    print(
        f"Vector Store created with {count} vectors and in the location {DB} and collection one with dimension {len(collects.get(limit=1, include=["embeddings"])["embeddings"][0])} "
    )
    return vector_store


if __name__ == "__main__":
    docs = load_documents()
    chunks = make_chunks(docs)
    encode_chunks(chunks)
    print(f"Ingestion Completed")
