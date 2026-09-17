import html
import os
import traceback
import gradio as gr
from rag.answer import chat

# ---------------------------------------------------------------------------
# Force light theme (Gradio otherwise follows the OS/browser color scheme,
# which is what produced the half-black, low-contrast layout).
# ---------------------------------------------------------------------------
force_light_js = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }
}
"""

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
custom_css = """
:root, .dark {
    --accent: #4f46e5 !important;
    --accent-light: #eef2ff !important;
    --border: #e5e7eb !important;
    --text-muted: #6b7280 !important;
    --bg-page: #f6f7fb !important;
    --body-background-fill: #f6f7fb !important;
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #ffffff !important;
    --block-background-fill: #ffffff !important;
    --body-text-color: #111827 !important;
    --body-text-color-subdued: #4b5563 !important;
    --input-background-fill: #ffffff !important;
    --neutral-50: #ffffff !important;
}

body, .gradio-container {
    background: var(--bg-page) !important;
    color: #111827 !important;
}

.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
}

#header {
    text-align: center;
    padding: 8px 0 16px 0;
}
#header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
}
#header em {
    color: #4b5563 !important;
    font-size: 0.95rem;
}

#chat-col, #sidebar {
    background: #ffffff !important;
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    padding: 14px;
}

#sidebar {
    max-height: 640px;
    overflow-y: auto;
}
#sidebar h3 {
    margin-top: 0;
    color: #111827 !important;
}

/* Chat bubbles */
.message.user {
    background: var(--accent) !important;
    color: #ffffff !important;
}
.message.bot {
    background: #f3f4f6 !important;
    color: #111827 !important;
}

/* Textbox */
textarea, input[type="text"] {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid var(--border) !important;
}

.chunk-card {
    background: var(--accent-light) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 12px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.chunk-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(79, 70, 229, 0.15);
}
.chunk-card summary {
    cursor: pointer;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    padding: 4px 0;
}
.chunk-card summary::-webkit-details-marker {
    display: none;
}
.chunk-card summary::before {
    content: "▸";
    color: var(--accent);
    margin-right: 2px;
    transition: transform 0.15s ease;
}
.chunk-card[open] summary::before {
    transform: rotate(90deg);
}
.chunk-source {
    font-size: 0.72rem;
    color: var(--accent) !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.chunk-badge {
    font-size: 0.68rem;
    color: #4338ca !important;
    background: #e0e7ff;
    border-radius: 999px;
    padding: 2px 8px;
    font-weight: 600;
}
.chunk-content {
    font-size: 0.88rem;
    color: #1f2937 !important;
    line-height: 1.5;
    white-space: pre-wrap;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed var(--border);
}
.chunk-empty {
    color: #6b7280 !important;
    text-align: center;
    padding: 24px 8px;
    font-size: 0.9rem;
}

/* Responsive: stack sidebar under chat on narrow screens */
@media (max-width: 900px) {
    #sidebar {
        max-height: 320px;
        margin-top: 12px;
    }
}
"""

EMPTY_SIDEBAR = "<div class='chunk-empty'>Retrieval sources will appear here once you ask a question.</div>"


def format_docs(docs):
    """Turn retrieved LangChain Document objects into styled, collapsible HTML cards.

    Doesn't assume a fixed metadata schema - pulls whatever source/page/etc.
    fields are actually present on each Document and falls back gracefully
    when a field is missing.
    """
    if not docs:
        return EMPTY_SIDEBAR

    SOURCE_KEYS = ("source", "file_path", "filename", "file_name", "path", "title")
    BADGE_KEYS = ("page", "page_number", "row", "chunk", "chunk_id", "score")

    cards = []
    for i, doc in enumerate(docs, 1):
        content = (
            html.escape((doc.page_content or "").strip()) or "<em>Empty chunk</em>"
        )
        meta = doc.metadata or {}

        raw_source = next((meta[k] for k in SOURCE_KEYS if meta.get(k)), None)
        source_name = (
            html.escape(os.path.basename(str(raw_source)))
            if raw_source
            else "Reference Document"
        )

        badges = "".join(
            f"<span class='chunk-badge'>{html.escape(str(k))}: {html.escape(str(meta[k]))}</span>"
            for k in BADGE_KEYS
            if meta.get(k) not in (None, "")
        )

        cards.append(f"""
            <details class="chunk-card" {"open" if i == 1 else ""}>
                <summary>
                    <span class="chunk-source">Source {i} · {source_name}</span>
                    {badges}
                </summary>
                <div class="chunk-content">{content}</div>
            </details>
            """)
    return "".join(cards)


def respond(message, history):
    """Main interaction logic: calls the backend and updates the UI."""
    message = (message or "").strip()
    if not message:
        return history, EMPTY_SIDEBAR, history

    history = history or []

    try:
        answer, docs = chat(message, history)
        print(f"[ServiceAssist] retrieved {len(docs)} chunk(s) for: {message!r}")
    except Exception as exc:  # surface backend errors in the chat instead of crashing
        traceback.print_exc()  # full traceback in the terminal for real debugging
        answer, docs = f"⚠️ Something went wrong while answering: {exc}", []

    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ]

    return history, format_docs(docs), history


def clear_chat():
    return [], EMPTY_SIDEBAR, []


with gr.Blocks(
    css=custom_css,
    js=force_light_js,
    title="ServiceAssist RAG",
    theme=gr.themes.Soft(primary_hue="indigo"),
) as demo:
    history_state = gr.State([])

    with gr.Column(elem_id="header"):
        gr.HTML("<h1>🤖 ServiceAssist</h1><em>Your ServiceNow Expert Helper</em>")

    with gr.Row(equal_height=True):
        with gr.Column(scale=3, elem_id="chat-col"):
            chatbot = gr.Chatbot(
                value=[],
                type="messages",
                label="Conversation",
                height=520,
                avatar_images=(None, None),
                show_copy_button=True,
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Ask me about ServiceNow scripting...",
                    show_label=False,
                    scale=9,
                    autofocus=True,
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)

            clear = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")

        with gr.Column(scale=1):
            gr.Markdown("### 📚 Retrived Chunks")
            chunks_display = gr.HTML(value=EMPTY_SIDEBAR)

    # --- Event Handlers ---
    msg.submit(
        respond,
        inputs=[msg, history_state],
        outputs=[chatbot, chunks_display, history_state],
    ).then(lambda: "", None, [msg])

    submit_btn.click(
        respond,
        inputs=[msg, history_state],
        outputs=[chatbot, chunks_display, history_state],
    ).then(lambda: "", None, [msg])

    clear.click(
        clear_chat,
        None,
        [chatbot, chunks_display, history_state],
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)
