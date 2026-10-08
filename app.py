import os
import gradio as gr
from rag_engine import RAGEngine

engine = RAGEngine()

def chat_response(message, history):
    result = engine.ask(message)
    return result["answer"]

demo = gr.ChatInterface(
    fn=chat_response,
    title="SASTRA University HR Policy Assistant",
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)