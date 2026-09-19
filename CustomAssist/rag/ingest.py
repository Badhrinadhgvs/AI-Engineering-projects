import os
from pathlib import Path
from dotenv import load_dotenv
from .improve import improve
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from logs.logger import logging

try:
    load_dotenv(override=True)
    logging.info("API Key is loaded succesfully")
except Exception as e:
    logging.error(f"Issue in loading API Key : {e}")


EMBEND_MODEL = "gemini-embedding-2-preview"
VECTOR_KB = str(Path(__file__).parent.parent / "vector_db")


def load_data_final(raw):
    try:
        data = process_improve(raw)
        chunks = chunk_data(data)
        vectorize_and_store(chunks)
        logging.info("Vector database Created Successfully")
    except Exception as e:
        logging.error(f"Error Occured while loading {e}")
        raise Exception(f"Error Loading the Data and Vectorizing: {e}")


def process_improve(raw):
    # Run the enrichment pipeline once per upload. Calling it twice wastes time
    # and can produce two different versions of the same document.
    improved = improve(raw)
    logging.info("Data Improved Succesfully")
    return improved


def chunk_data(data):
    if not data or not data.strip():
        logging.error("No data is passed.")
        return []
    # Keep chunks useful even for short documents. The original proportional
    # calculation could produce a zero-sized splitter for small PDFs.
    chunk_size = max(500, min(4000, len(data) // 4 or len(data)))
    chunk_overlap = min(chunk_size // 5, max(0, chunk_size // 8))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.create_documents([data])  # returns List[Document]
    logging.info("Chunks Created Succesfully")
    return chunks


def vectorize_and_store(chunks):
    if not chunks:
        logging.error("Chunks are not present/passed")
        raise ValueError("No text was found to index.")
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEND_MODEL)
    if os.path.exists(VECTOR_KB):
        Chroma(
            persist_directory=VECTOR_KB, embedding_function=embeddings
        ).delete_collection()
    vector = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_KB,
    )
    logging.info("Successfully embedded and database created")
    collection = vector._collection
    count = collection.count()
    sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    print(
        f"The Vectors are successfully created and added into the Database, with count {count} and {len(sample_embedding)} Dimensions"
    )
