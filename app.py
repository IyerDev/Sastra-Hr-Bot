import os
import gradio as gr
from rag_engine import RAGEngine

engine = RAGEngine()

WELCOME_MESSAGE = """**Hello! Welcome to the SASTRA University HR Policy Assistant.**

I can help you answer questions based strictly on official university HR policies with exact section citations.

What would you like to know today?"""

def chat_response(message, history):
    result = engine.ask(message)
    return result["answer"]

# Preload the assistant's first message bubble
chatbot = gr.Chatbot(
    value=[{"role": "assistant", "content": WELCOME_MESSAGE}]
)

demo = gr.ChatInterface(
    fn=chat_response,
    chatbot=chatbot,
    title="SASTRA University HR Policy Assistant",
    examples=[
        "How many days of casual leave can I take in a year?",
        "What are the rules for maternity leave?",
        "What happens if I am late three times in a month?",
    ],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)