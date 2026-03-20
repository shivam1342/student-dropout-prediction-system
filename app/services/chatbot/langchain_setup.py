"""Chroma setup helpers for chatbot retrieval."""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

from app.services.chatbot.config import EMBEDDING_MODEL, CHROMA_PERSIST_DIR


def _build_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def create_vector_store(
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    collection_name: str = "student_chatbot",
):
    """Create a persisted Chroma vector store for the current retrieval call."""
    import chromadb
    from langchain_chroma import Chroma

    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    embeddings = _build_embeddings()
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Recreate per-user collection each call so retrieval uses only fresh context.
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    vectorstore = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    return vectorstore
