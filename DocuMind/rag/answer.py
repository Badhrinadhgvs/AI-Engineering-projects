import os
from pathlib import Path
from dotenv import load_dotenv
from .rerank import rerank_chunks
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage
from logs.logger import logging

load_dotenv(override=True)
EMBEND_MODEL = "gemini-embedding-2-preview"
VECTOR_KB = str(Path(__file__).parent.parent / "vector_db")

embedding = GoogleGenerativeAIEmbeddings(model=EMBEND_MODEL)
vectorstore = Chroma(persist_directory=VECTOR_KB, embedding_function=embedding)
retriver = vectorstore.as_retriever()

SYS = "You are an helper for knowledge based Agent, your duty is to enhance, improve and expand the question which will be asked by the user. which helps in good retrieval of context from the knowledge. Strictly only provide the new question other than that nothing"
USER = "Here is the question which you have to improve, enhance and expand, Only Provide the question as output. Do not add extra content other than that\
  Question:\
    {question}"


def enhance_question(question):
    mess = [SystemMessage(SYS)]
    mess.append(HumanMessage(USER.format(question=question)))

    enhancer = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash", max_tokens=None, timeout=None
    )
    res = enhancer.invoke(mess)
    logging.info("Question enhanced successfully")
    return str(res.content)


def get_question(question, history):
    """Build a retrieval query from prior user turns and the current question."""
    previous_questions = "\n\n".join(
        h["content"] for h in history if h.get("role") == "user"
    )
    enhanced = enhance_question(question)
    logging.info("New question created")
    return f"{previous_questions}\n\n{enhanced}".strip()


def get_context(question, history):
    q = get_question(question, history)
    chunks = retriver.invoke(q)
    chunks = rerank_chunks(history, question, chunks)
    logging.info("Chunks created and sent")
    return chunks
