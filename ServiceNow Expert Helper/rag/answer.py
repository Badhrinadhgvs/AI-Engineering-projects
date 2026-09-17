import os
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages
from langchain_ollama import ChatOllama

embeddings = HuggingFaceEmbeddings(model="all-MiniLM-L6-v2")
MODEL = "gemma4:31b-cloud"
MAX_K = 5
DB = str(Path(__file__).parent.parent / "vector_db")
llm = ChatOllama(model=MODEL)
SYSTEM_PROMPT = """
You are an Helpful Knowledgable Servicenow Assistant, Your main duty is to help the user who will approaching you in making the custom software apps using servicenow. You will be provided with the relevant context, Use the context and help the user to make things effectively. If needed generate the servicenow scripting code in Java Script.
Respond in an Accurate, Positive and in a friendly name. Your name is *ServiceAssist*
And do not respond with larger text, It will be good ify you respond in simple straight and correct point. You will be deployed at the end cutomers remember that. Respond in markdown only


Context:
{context}
"""
vector_db = Chroma(persist_directory=DB, embedding_function=embeddings)

retriver = vector_db.as_retriever(search_kwargs={"k": MAX_K})


def get_final_ques(ques, history):
    prev = "\n\n".join(h["content"] for h in history if h["role"] == "user")
    return prev + ques


def get_rel_context(q, his):
    que = get_final_ques(q, his)
    return retriver.invoke(que)


def chat(message, history):
    docs = get_rel_context(message, history)
    context = "\n\n".join(i.page_content for i in docs)
    sys_pr = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(sys_pr)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(message))
    res = llm.invoke(messages)
    return res.content, docs
