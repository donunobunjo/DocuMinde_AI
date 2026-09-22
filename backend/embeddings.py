from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_function():
    """
    Creates the embedding model used to convert document
    chunks and user questions into vectors.

    The embedding model runs as part of the backend.
    It does not require Ollama.
    """

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )