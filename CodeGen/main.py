import gradio as gr
from IPython.display import Markdown, display
from app.LLM import CodeGen


def main() -> None:

    with gr.Blocks(title=f"LangTranslate") as ui:
        with gr.Row():
            python = gr.Code(label="Python code")
            target = gr.Code(label="Target Code")
        with gr.Row():
            lang = gr.Textbox(label="Enter Target Language", lines=1, value="Cpp")
            convert = gr.Button("Convert Code")
        convert.click(execute, inputs=[python, lang], outputs=[target])
    ui.launch(inbrowser=True)


def execute(code, lang):
    c = CodeGen(code, lang)
    return c.main()


if __name__ == "__main__":
    main()
