from langchain_community.vectorstores import Chroma

from embeddings import HuggingFaceEmbeddings


CHROMA_PATH = "chroma_db"


def get_embedding_function():
    """
    Create the Hugging Face embedding client.
    """

    return HuggingFaceEmbeddings()


def get_vector_store(session_id: str):
    """
    Return a Chroma vector store dedicated to one user session.
    """

    embedding_function = get_embedding_function()

    return Chroma(
        collection_name=f"rag_{session_id}",
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )