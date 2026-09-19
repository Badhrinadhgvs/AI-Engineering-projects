import json
import re
from langchain_ollama import ChatOllama
from logs.logger import logging
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

RERANK_SYS_PR = """
# ROLE
You are a Relevance Reranking Agent in a RAG pipeline. You receive a user's 
conversation history (current and prior questions) along with a set of 
candidate text chunks retrieved via vector similarity search. Your job is to 
re-score and rank these chunks by how genuinely relevant and useful each one 
is for answering the user's CURRENT question, using the conversation history 
for context (e.g., resolving follow-up questions, pronouns, or implied topics).

# INPUT
You will receive:
1. CONVERSATION HISTORY: prior user messages, oldest to most recent.
2. CURRENT QUESTION: the user's latest message, which you are ranking chunks 
   against.
3. CANDIDATE CHUNKS: a list of retrieved chunks, each with an ID and source 
   reference (e.g., page number).

# TASK
1. Read the conversation history to understand the full context of what the 
   user is asking — especially if the current question is a follow-up, 
   contains pronouns ("it", "that", "the second one"), or is otherwise 
   ambiguous without prior turns.
2. Evaluate each candidate chunk for how directly and specifically it helps 
   answer the CURRENT question, in light of that context.
3. Assign each chunk a relevance score from 0 to 10:
   - 9-10: Directly and completely answers the question.
   - 6-8: Relevant and useful, but partial or supporting context.
   - 3-5: Tangentially related; unlikely to be needed but not irrelevant.
   - 0-2: Not relevant to the current question, even with conversation context.
4. Rank all chunks from most to least relevant based on these scores.

# RULES
- Judge relevance to the CURRENT question as informed by history — not to the 
  conversation as a whole. Older topics that are no longer relevant to the 
  current question should score low even if they matched the original vector 
  search.
- Do not rewrite, summarize, or alter chunk content — you are only scoring and 
  ranking, not editing.
- Do not use outside knowledge to judge correctness of chunk content — you are 
  ranking by topical/contextual relevance only, not factual accuracy.
- If two chunks are near-duplicates covering the same information, you may 
  note this, but still score each independently.

# OUTPUT FORMAT
Return ONLY valid JSON, no other text, in this exact structure:
{
  "ranked_chunks": [
    {"chunk_id": "<id>", "score": <0-10>, "reason": "<one short phrase>"},
    ...
  ]
}
Order the array from highest to lowest score.
"""

RERANK_USER_PR = """
CONVERSATION HISTORY:
{conversation_history}

CURRENT QUESTION:
{current_question}

CANDIDATE CHUNKS:
{candidate_chunks}

---
TASK:
Score and rank the CANDIDATE CHUNKS above by relevance to the CURRENT QUESTION, 
using the CONVERSATION HISTORY for context. Return only the JSON output as 
specified in your instructions.
"""
llm = ChatOllama(
    model="gpt-oss:120b-cloud",  # or "gpt-oss:20b" / "gpt-oss:120b" depending on what you pulled
    temperature=0,
    format="json",  # Ollama-level hint to bias output toward valid JSON
)


def format_conversation_history(messages: list[str]) -> str:
    if not messages:
        return "(no prior messages — this is the first question)"
    return "\n".join(f"{i+1}. {msg}" for i, msg in enumerate(messages))


def format_candidate_chunks(chunks: list[Document]) -> str:
    """Format LangChain Document objects for the rerank prompt."""
    formatted = []
    for doc in chunks:
        page = doc.metadata.get(
            "page", "?"
        )  # falls back gracefully if metadata is empty
        formatted.append(f"[chunk_id: {doc.id} | Page {page}]\n{doc.page_content}")
    return "\n\n".join(formatted)


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, re.DOTALL)
        if match:
            raw = match.group(1)
    if not raw.strip().startswith("{"):
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)
    return json.loads(raw)


def rerank_chunks(
    conversation_history: list[str], current_question: str, chunks: list[Document]
) -> list[Document]:
    """
    Reranks LangChain Document chunks using conversation history + current question.
    Returns the Document objects re-sorted by relevance, with score/reason
    attached to each doc's metadata.
    """
    user_prompt = RERANK_USER_PR.format(
        conversation_history=format_conversation_history(conversation_history),
        current_question=current_question,
        candidate_chunks=format_candidate_chunks(chunks),
    )

    response = llm.invoke(
        [
            SystemMessage(content=RERANK_SYS_PR),
            HumanMessage(content=user_prompt),
        ]
    )

    try:
        result = extract_json(response.content)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ValueError(f"Failed to parse reranker output:\n{response.content}") from e

    # Lookup by Document.id
    doc_lookup = {doc.id: doc for doc in chunks}

    ranked = []
    for item in result.get("ranked_chunks", []):
        cid = item.get("chunk_id")
        if cid in doc_lookup:
            doc = doc_lookup[cid]
            doc.metadata["score"] = item.get("score")
            doc.metadata["reason"] = item.get("reason")
            ranked.append(doc)
    logging.info("Chunks are reranked and sent")
    return ranked
