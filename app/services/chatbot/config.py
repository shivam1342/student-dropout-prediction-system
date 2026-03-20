"""Configuration for chatbot service."""
import os

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
CHATBOT_TOP_K = int(os.getenv("CHATBOT_TOP_K", "3"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Persisted Chroma store location (inside project instance folder by default)
CHROMA_PERSIST_DIR = os.getenv(
	"CHROMA_PERSIST_DIR",
	os.path.join("instance", "chroma_db"),
)
CHROMA_COLLECTION_PREFIX = os.getenv("CHROMA_COLLECTION_PREFIX", "student_chatbot")
