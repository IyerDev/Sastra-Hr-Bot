import os
from dotenv import load_dotenv
from groq import Groq
from retriever import PolicyRetriever

load_dotenv()

MODEL_NAME = "qwen/qwen3.8-27b"
SYSTEM_INSTRUCTION = """You are the official SASTRA University HR Policy Assistant.
Your task is to answer user queries strictly using the university HR policy context provided below.

Rules to follow:
1. Grounding: Answer ONLY based on facts directly stated in the context. If the context does not contain the answer, say: "The SASTRA HR Policy does not contain information regarding this."
2. Citations: Always cite the exact section numbers (e.g. [Section 10.9.1 - Casual Leave] or [Section 5 - Pay & Allowances]).
3. Clarity: Structure your answer using neat bullet points.
4. Professional tone: Direct, helpful, and concise.
5. Proactive Follow-up: At the very end of your answer, add a separate line asking a relevant follow-up question based on the topic. 
   For example:
   "Would you like to know more about the application procedure or related leave rules?"
"""

class RAGEngine:
    def __init__(self, model_name=MODEL_NAME):
        print("Loading Policy Retriever...")
        self.retriever = PolicyRetriever()
        self.model_name = model_name
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def ask(self, query: str, top_k: int = 3):
        # 1. RETRIEVE matching chunks (same as before)
        search_results = self.retriever.search(query, top_k=top_k)
        chunks = [chunk for _, chunk in search_results]

        if not chunks:
            return {
                "query": query,
                "answer": "No relevant policy sections could be found for your query.",
                "sources": [],
                "model": self.model_name
            }

        # 2. CONSTRUCT CONTEXT (same as before)
        context_parts = [
            f"[Source {i}: {chunk['full_heading']}]\n{chunk['content']}\n"
            for i, chunk in enumerate(chunks, 1)
        ]
        full_context = "\n".join(context_parts)

        # 3. GENERATE via Groq Cloud
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {
                        "role": "user",
                        "content": f"=== RELEVANT SASTRA HR POLICY CONTEXT ===\n{full_context}\n\n=== USER QUESTION ===\n{query}\n\n=== ANSWER (strictly grounded with section citations) ==="
                    }
                ],
                temperature=0.2,
            )
            answer = completion.choices[0].message.content.strip()

        except Exception as e:
            answer = f"Groq API Error: {str(e)}"

        return {
            "query": query,
            "answer": answer,
            "sources": [c["full_heading"] for c in chunks],
            "model": self.model_name
        }