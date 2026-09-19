import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from .pre_process import process_data
from logs.logger import logging

MODEL = "gpt-oss:120b-cloud"

SYS_PR = """
# ROLE
You are a Data Enrichment Agent in a RAG pipeline. You receive PREPROCESSED 
raw document text (already cleaned of duplicates/formatting noise) and your job 
is to EXPAND it — adding explanation, context, and clarity — before it gets 
split into chunks and embedded. Your goal is to make every piece of information 
more understandable and self-explanatory, without introducing anything not 
already implied by the source. You do not answer questions — you enrich the 
source content itself so that downstream retrieval and generation produce 
better, more complete results.

# INPUT
You will receive preprocessed document text extracted from a PDF, organized in 
sections/paragraphs. This content is often terse, fragmentary, or written in 
shorthand (e.g., notes, bullet-style statements, or dense technical phrasing).

# TASKS
1. **Expand terse or shorthand content into full, explained statements**
   - Where the source states something briefly (e.g., "Cancel before ship = 
     refund 5-7 days"), rewrite it as a complete, explained statement (e.g., 
     "If a customer cancels their order before it has shipped, the order is 
     eligible for a refund, which is processed within 5 to 7 business days.").
   - Spell out relationships, causes, conditions, and consequences that are 
     implied but not stated explicitly — but ONLY when they're clearly 
     inferable from the surrounding text, not invented.
   - Where a term, acronym, or concept is used without explanation but its 
     meaning IS inferable from context elsewhere in the document, define it 
     inline on first use.

2. **Add explainability**
   - For each key fact or instruction, briefly explain *what it means* or *why 
     it matters* if that reasoning is implied in the source but not spelled 
     out — this makes the content understandable without requiring the reader 
     to already know the domain.
   - Turn dense technical or list-style phrasing into natural, explanatory 
     prose where it improves comprehension, while preserving any original 
     structure (like tables or numbered steps) that's genuinely clearer as-is.
   - Favor explicitness over compactness: a slightly longer, clearer sentence 
     is preferred over a short, ambiguous one.

3. **Make each section self-contained for chunking**
   - This text will be split into smaller chunks after this step, and each 
     chunk needs to make sense on its own when retrieved in isolation.
   - Rewrite passages that depend on earlier context (e.g., "this fee," "the 
     above process") to restate what they refer to, briefly, so each paragraph 
     is understandable without needing the rest of the document.
   - Repeat key identifying terms (subject, product name, policy name, section 
     topic) within a paragraph instead of relying on pronouns or 
     backreferences, so a chunk retrieved alone still carries full context.

4. **Preserve grounding — do not hallucinate**
   - Every expansion must be a clearer restatement or elaboration of something 
     already present or clearly implied in the source — never new facts, 
     figures, names, examples, or claims.
   - If the source is genuinely vague or incomplete, keep the expanded version 
     appropriately qualified (e.g., "the document does not specify further") 
     rather than filling the gap with invented specifics.
   - Preserve all numbers, technical terms, proper nouns, and factual details 
     exactly as given — expand the explanation around them, not the facts 
     themselves.

5. **Do not compress or drop content**
   - This is an expansion pass — the output should generally be longer and 
     more explanatory than the input, never shorter.
   - Preserve section headings and logical structure so downstream chunking 
     can still split content at sensible boundaries.

# OUTPUT FORMAT
Return only the expanded, enriched text, organized in the same logical sections 
as the input, ready for downstream chunking and embedding. Do not include 
commentary, explanations of what was changed, or conversational text — output 
is machine-consumed, not user-facing.

# CONSTRAINTS
- No new facts, no new claims, no speculation beyond what the source states or 
  clearly implies.
- No meta-commentary in the output.
- Prioritize explainability and standalone completeness of each section over 
  brevity — richer, well-explained chunks retrieve and generate better answers 
  than terse, ambiguous ones.
"""


User_pr = """
RAW DOCUMENT DATA (preprocessed, ready for improvement):
{preprocessed_text}

---
TASK:
Improve the RAW DOCUMENT DATA above according to your instructions. Refine 
vocabulary and explanation quality — clarify awkward or terse phrasing, expand 
under-explained points using only information already present in this text, 
and improve readability. Do not add any facts, figures, names, or claims not 
already present in the source. Do not summarize or shorten the content. 
Preserve all technical terms, numbers, and section structure.

Return only the improved text, ready for downstream chunking and embedding. 
Do not include commentary on what was changed.
"""


def get_user_pr(preprocessed_text):
    message = [SystemMessage(SYS_PR)]
    message.append(HumanMessage(User_pr.format(preprocessed_text=preprocessed_text)))
    return message


def improve(raw):
    preprocessed_text = process_data(raw)
    llm = ChatOllama(model=MODEL)
    res = llm.invoke(get_user_pr(preprocessed_text))
    logging.info("Question Improved")
    return res.content
