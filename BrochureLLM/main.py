import gradio as gr
from Components.LLM import LLM

def main():
    comp_in = gr.Textbox(label="Enter the company name:", lines=3)
    comp_url = gr.Textbox(label="Enter URL:", info="The url has to start with either http:// (or) https://", lines=2)
    selc_model = gr.Dropdown(
        label="Select the model:",
        choices=["nemotron-3-nano:30b-cloud", "gemma4:cloud", "gpt-oss:20b-cloud"]
    )
    output = gr.Markdown(label="Response")

    llm = LLM()

    view = gr.Interface(
        title="Brochure Gen",
        inputs=[comp_in, comp_url, selc_model],
        outputs=[output],
        fn=llm.create_brochure,      
        examples=[
            ["Hugging Face", "https://huggingface.co", "nemotron-3-nano:30b-cloud"],
            ["Edward Donner", "https://edwarddonner.com", "gemma4:cloud"],
            ["NECN", "https://necn.ac.in", "gpt-oss:20b-cloud"],
        ],
        flagging_mode="never",
    )
    view.launch()

if __name__ == "__main__":
    main()