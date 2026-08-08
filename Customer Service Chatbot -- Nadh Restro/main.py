import gradio as gr
from Components.CSLLM import chat

chat_view = gr.ChatInterface(
  fn=chat,
  type="messages",
  title="Nadh Restro"
)


if __name__=="__main__":
  chat_view.launch(inbrowser=True)
