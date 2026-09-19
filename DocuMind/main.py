"""Streamlit interface for uploading a PDF and chatting with its contents."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from logs.logger import logging

load_dotenv(override=True)

ROOT = Path(__file__).parent
VECTOR_DB = ROOT / "vector_db"


def configure_page() -> None:
    st.set_page_config(
        page_title="DocuMind · PDF Assistant",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {
            color-scheme: light;
            --ink: #1c1917;
            --muted: #6b6259;
            --navy: #241a2e;
            --teal: #b45309;
            --teal-hover: #92400e;
            --cyan: #c2410c;
            --panel-bg: rgba(255, 255, 255, 0.90);
            --panel-border: #e7ded0;
        }
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            color-scheme: light !important;
        }
        .stApp {
            background: linear-gradient(145deg, #fdfbf6 0%, #f9f1e7 50%, #fdf3e7 100%);
            color: var(--ink);
            min-width: 320px;
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"] { background: transparent !important; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--navy); }
        .hero { padding: 1.2rem 0 1rem; }
        .eyebrow {
            color: var(--cyan);
            font-size: .8rem;
            font-weight: 700;
            letter-spacing: .14em;
            text-transform: uppercase;
        }
        .hero h1 { font-size: clamp(2rem, 4vw, 3.35rem); margin: .35rem 0 .6rem; letter-spacing: -.04em; color: #1c1917; }
        .hero p { color: var(--muted); font-size: 1.05rem; max-width: 720px; line-height: 1.65; }
        .panel {
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--panel-border);
            border-radius: 20px;
            padding: 1.35rem 1.5rem;
            box-shadow: 0 10px 30px -5px rgba(28, 25, 23, 0.06), 0 4px 10px -2px rgba(28, 25, 23, 0.03);
        }
        .tip {
            background: #fff7ed;
            border-left: 4px solid var(--teal);
            border-radius: 10px;
            padding: .85rem 1rem;
            color: #7c2d12;
            font-size: .92rem;
            box-shadow: 0 1px 3px rgba(180, 83, 9, 0.06);
        }
        /* Light-only sidebar */
        [data-testid="stSidebar"] {
            background: #fffdf9 !important;
            border-right: 1px solid #e7ded0;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--navy) !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: var(--ink);
        }
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] small {
            color: var(--muted) !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: #e7ded0 !important;
        }
        /* File Uploader in Sidebar */
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background: #faf6ee !important;
            border: 1.5px dashed #d6c8ae !important;
            border-radius: 12px !important;
            padding: 1rem 0.75rem !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
            background: #fff7ed !important;
            border-color: var(--teal) !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] div {
            color: var(--muted) !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {
            fill: var(--teal) !important;
            stroke: var(--teal) !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            background: #ffffff !important;
            color: var(--ink) !important;
            border: 1px solid #d6c8ae !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
            background: #fff7ed !important;
            color: var(--teal-hover) !important;
            border-color: var(--teal) !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
            background: #faf6ee !important;
            border: 1px solid #e7ded0 !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * {
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] [data-testid="stAlert"] {
            background: #fff7ed !important;
            border: 1px solid #fde3c7 !important;
            color: #7c2d12 !important;
            border-radius: 10px !important;
        }
        /* Buttons */
        .stButton > button,
        button[data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            border-radius: 10px !important;
            border: none !important;
            background: linear-gradient(135deg, #b45309 0%, #c2410c 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.25rem !important;
            box-shadow: 0 4px 14px rgba(180, 83, 9, 0.28) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        button[kind="primary"]:hover {
            background: linear-gradient(135deg, #92400e 0%, #9a3412 100%) !important;
            box-shadow: 0 6px 20px rgba(180, 83, 9, 0.38) !important;
            transform: translateY(-1px) !important;
            color: white !important;
        }
        .stButton > button:active,
        button[data-testid="stBaseButton-primary"]:active,
        button[kind="primary"]:active {
            transform: translateY(0) !important;
        }
        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(8px);
            border: 1px solid #e7ded0;
            border-radius: 16px;
            padding: 1rem 1.25rem;
            margin-bottom: .85rem;
            box-shadow: 0 2px 8px rgba(28, 25, 23, 0.04);
            transition: border-color 0.2s ease;
        }
        [data-testid="stChatMessage"]:hover {
            border-color: #d6c8ae;
        }
        /* Status and Info widgets */
        [data-testid="stStatusWidget"] {
            border-radius: 14px !important;
            border: 1px solid #d6c8ae !important;
            background: #ffffff !important;
        }
        /* Chat input: roomy, readable, and responsive */
        [data-testid="stChatInput"] {
            border: 0 !important;
            background: transparent !important;
        }
        [data-testid="stChatInput"] > div {
            border: 1px solid #d6c8ae !important;
            border-radius: 16px !important;
            background: #ffffff !important;
            box-shadow: 0 8px 24px rgba(28, 25, 23, 0.10) !important;
            padding: .25rem .4rem .25rem .75rem !important;
            transition: border-color .2s ease, box-shadow .2s ease !important;
        }
        [data-testid="stChatInput"] > div:focus-within {
            border-color: var(--teal) !important;
            box-shadow: 0 0 0 3px rgba(180, 83, 9, 0.14), 0 8px 24px rgba(28, 25, 23, 0.10) !important;
        }
        [data-testid="stChatInput"] textarea {
            min-height: 2.8rem !important;
            max-height: 9rem !important;
            padding: .7rem .25rem !important;
            border: 0 !important;
            background: transparent !important;
            color: var(--ink) !important;
            font-size: 1rem !important;
            line-height: 1.45 !important;
            box-shadow: none !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #a89a80 !important;
        }
        [data-testid="stChatInputSubmitButton"] button {
            width: 2.35rem !important;
            height: 2.35rem !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            background: var(--teal) !important;
            transition: background .2s ease, transform .2s ease !important;
        }
        [data-testid="stChatInputSubmitButton"] button:hover {
            background: var(--teal-hover) !important;
            transform: translateY(-1px) !important;
        }
        @media (max-width: 900px) {
            [data-testid="stSidebar"] { min-width: 16rem; }
            .panel { padding: 1.1rem; }
            .hero { padding-top: .75rem; }
        }
        @media (max-width: 640px) {
            [data-testid="stSidebar"] { min-width: 0; }
            .hero h1 { font-size: 2.1rem; }
            .hero p { font-size: .98rem; }
            .panel { border-radius: 14px; padding: 1rem; }
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: .75rem !important;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            [data-testid="stChatInput"] > div { border-radius: 13px !important; }
            [data-testid="stChatInput"] textarea { font-size: .95rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def extract_pdf(uploaded_file: Any) -> tuple[str, int]:
    reader = PdfReader(uploaded_file)
    pages: list[str] = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"\n\n--- Page {number} ---\n{text}")
    logging.info("PDF extraction completed")
    return "".join(pages).strip(), len(reader.pages)


def file_id(uploaded_file: Any) -> str:
    return hashlib.sha256(uploaded_file.getvalue()).hexdigest()


def index_document(text: str) -> None:
    from rag.ingest import load_data_final

    load_data_final(text)


def retrieve_documents(question: str, history: list[dict[str, str]]):
    """Use answer.py's enhanced retrieval, with a direct retriever fallback."""
    try:
        import importlib
        from rag import answer

        # Reopen the Chroma handle after ingest replaced the collection.
        answer = importlib.reload(answer)
        logging.error("Issue during retrieval")
        return answer.get_context(question, history), "enhanced retrieval"
    except Exception as enhanced_error:
        st.session_state["last_retrieval_note"] = str(enhanced_error)
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
        store = Chroma(persist_directory=str(VECTOR_DB), embedding_function=embeddings)
        logging.info("Retrieval Completed")
        return store.similarity_search(question, k=5), "vector similarity retrieval"


def _extract_text(content: Any) -> str:
    """Normalize a chat model's `.content` into plain text.

    Some models return a plain string; others return a list of content
    blocks (e.g. text blocks alongside thinking/signature metadata). This
    pulls out only the text parts and ignores everything else.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)


def generate_answer(
    question: str, context_docs: list[Any], history: list[dict[str, str]]
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI

    context = "\n\n".join(doc.page_content for doc in context_docs)
    prior = "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])
    system = """You are a precise document question-answering assistant.
Answer using only the supplied document context. If the answer is not present,
say that the document does not provide enough information. Do not invent facts.
Be concise but explain the reasoning when useful. Use markdown when it improves
readability. Do not mention retrieval, prompts, or internal tools.

DOCUMENT CONTEXT:
{context}

RECENT CONVERSATION:
{prior}""".format(context=context, prior=prior or "(none)")
    model = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.2)
    response = model.invoke(
        [SystemMessage(content=system), HumanMessage(content=question)]
    )
    return _extract_text(response.content)


def render_sidebar() -> Any:
    with st.sidebar:
        st.markdown("## ✦ DocuMind")
        st.caption("A focused reading companion for your PDFs")
        st.divider()
        uploaded = st.file_uploader(
            "Upload a PDF", type=["pdf"], accept_multiple_files=False
        )
        if uploaded:
            st.success(f"{uploaded.name}")
            st.caption(f"{uploaded.size / 1024:.0f} KB · PDF document")
        st.divider()
        st.caption(
            "Your document is indexed locally in the Chroma vector database. Ask questions only after indexing finishes."
        )
        return uploaded


def main() -> None:
    configure_page()
    uploaded = render_sidebar()
    st.markdown(
        '<div class="hero"><div class="eyebrow">Private document intelligence</div>'
        "<h1>Read less. Understand more.</h1>"
        "<p>Upload a PDF, build a searchable knowledge base, and ask grounded questions in a calm, focused workspace.</p></div>",
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "indexed_id" not in st.session_state:
        st.session_state.indexed_id = None

    if not uploaded:
        st.markdown(
            '<div class="panel"><h3>Start with a document</h3><p>Choose a PDF from the sidebar to extract its text and create your searchable index.</p><div class="tip">Tip: text-based PDFs work best. Scanned image-only PDFs need OCR before upload.</div></div>',
            unsafe_allow_html=True,
        )
        return

    current_id = file_id(uploaded)
    if st.session_state.indexed_id != current_id:
        try:
            text, page_count = extract_pdf(uploaded)
        except Exception as error:
            st.error(f"Could not read this PDF: {error}")
            return
        if not text:
            st.warning(
                "No selectable text was found. This PDF may be scanned; run OCR and upload it again."
            )
            return
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f'<div class="panel"><h3>{uploaded.name}</h3><p>{page_count} pages · {len(text):,} characters extracted</p></div>',
                unsafe_allow_html=True,
            )
        with col2:
            should_index = st.button(
                "Build knowledge base", type="primary", use_container_width=True
            )
        if should_index:
            with st.status("Preparing your document…", expanded=True) as status:
                st.write("Extracting and enriching the PDF text")
                try:
                    index_document(text)
                    st.session_state.indexed_id = current_id
                    st.session_state.messages = []
                    status.update(label="Knowledge base ready", state="complete")
                    st.rerun()
                except Exception as error:
                    status.update(label="Indexing failed", state="error")
                    st.error(f"Could not build the vector database: {error}")
        st.info("Click **Build knowledge base** to make this document searchable.")
        return

    st.markdown(
        '<div class="panel"><h3>Ask your document</h3><p>Answers are grounded in the indexed PDF.</p></div>',
        unsafe_allow_html=True,
    )
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your PDF…")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching the document…"):
                try:
                    docs, retrieval_mode = retrieve_documents(
                        question, st.session_state.messages
                    )
                    reply = generate_answer(question, docs, st.session_state.messages)
                    st.markdown(reply)
                    st.caption(f"Source mode: {retrieval_mode}")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply}
                    )
                except Exception as error:
                    st.error(f"I could not answer that right now: {error}")


if __name__ == "__main__":
    logging.info("Application Starting...")
    main()
    logging.info("Application Ending...")
