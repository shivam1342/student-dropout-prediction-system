"""Retriever builder for user-scoped chatbot context."""
from __future__ import annotations

from typing import List, Dict, Any

from app.services.chatbot.config import CHATBOT_TOP_K, CHROMA_COLLECTION_PREFIX
from app.services.chatbot.langchain_setup import create_vector_store


def get_retriever(texts: List[str], metadatas: List[Dict[str, Any]], user_id: int):
    vectorstore = create_vector_store(
        texts,
        metadatas,
        collection_name=f"{CHROMA_COLLECTION_PREFIX}_{user_id}",
    )

    # Metadata filter anchored on authenticated user id.
    return vectorstore.as_retriever(
        search_kwargs={
            "k": CHATBOT_TOP_K,
            "filter": {"user_id": str(user_id)},
        }
    )
