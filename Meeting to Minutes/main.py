import gradio as gr
from app.LLM import MeetLLM


def process_audio(audio_file):
    """
    Process uploaded audio using the MeetLLM backend.
    """

    if audio_file is None:
        return "## Please upload an MP3 audio file first."

    try:
        # Create the backend object
        meeting = MeetLLM(audio_file)

        # Generate the summary
        result = meeting.summarize()

        if result:
            return result

        return "## No summary was generated."

    except Exception as e:
        return f"""
## Error

Something went wrong while processing the audio.

**Details:** `{str(e)}`
"""


def clear_all():
    """
    Clear the audio input and summary output.
    """
    return None, "Your summary will appear here..."


# ---------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------

with gr.Blocks(title="Meeting to Minutes", theme=gr.themes.Soft()) as demo:

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    gr.Markdown("""
# Meeting to Minutes

### AI-Powered Meeting Summarization

Upload your meeting recording and let AI:

1. Transcribe the meeting
2. Analyze the transcript
3. Extract important information
4. Generate a clear meeting summary

---
""")

    # -----------------------------------------------------
    # Main Layout
    # -----------------------------------------------------

    with gr.Row():

        # -------------------------------------------------
        # Left Side - Audio Input
        # -------------------------------------------------

        with gr.Column(scale=1):

            gr.Markdown("### Upload Meeting Audio")

            audio_input = gr.Audio(
                label="Meeting Recording",
                sources=["upload"],
                type="filepath",
                format="mp3",
            )

            gr.Markdown("""
**Supported format:** MP3

Upload your meeting recording and click **Generate Summary**.
""")

        # -------------------------------------------------
        # Right Side - Output
        # -------------------------------------------------

        with gr.Column(scale=1):

            gr.Markdown("### Meeting Summary")

            summary_output = gr.Markdown(value="Your summary will appear here...")

    # -----------------------------------------------------
    # Buttons
    # -----------------------------------------------------

    with gr.Row():

        generate_btn = gr.Button("Generate Summary", variant="primary", size="lg")

        clear_btn = gr.Button("Clear", variant="secondary", size="lg")

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    gr.Markdown("""
### Processing Information

The AI processing may take some time because the application first
transcribes the audio and then generates the meeting summary.
""")

    # -----------------------------------------------------
    # Generate Summary Event
    # -----------------------------------------------------

    generate_btn.click(
        fn=process_audio,
        inputs=audio_input,
        outputs=summary_output,
        # IMPORTANT:
        # Shows Gradio's loading animation while the
        # backend function is running.
        show_progress="full",
        # Show the loading animation specifically
        # on the summary output.
        show_progress_on=summary_output,
        # Scroll to the generated summary after completion.
        scroll_to_output=True,
    )

    # -----------------------------------------------------
    # Clear Event
    # -----------------------------------------------------

    clear_btn.click(fn=clear_all, inputs=[], outputs=[audio_input, summary_output])


# ---------------------------------------------------------
# Start Application
# ---------------------------------------------------------

if __name__ == "__main__":
    demo.launch()
