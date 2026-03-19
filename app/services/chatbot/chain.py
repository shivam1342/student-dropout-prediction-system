"""Build RAG chain using Chroma retriever and Groq LLM."""
from __future__ import annotations

from langchain.chains import RetrievalQA

from app.services.chatbot.llm import GroqLLM
from app.services.chatbot.prompts import get_prompt


def build_chain(retriever):
    llm = GroqLLM()
    prompt = get_prompt()

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )
