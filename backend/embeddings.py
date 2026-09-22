import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()


HF_TOKEN = os.getenv("HF_TOKEN")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)


client = InferenceClient(
    token=HF_TOKEN,
    provider="hf-inference",
    timeout=60
)


class HuggingFaceEmbeddings:
    """
    Generate embeddings using Hugging Face Inference API.

    The embedding model runs remotely, so the Render
    backend does not need to load a local ML model.
    """

    def embed_documents(self, texts):
        """
        Convert multiple document chunks into vectors.
        """

        if not texts:
            return []

        result = client.feature_extraction(
            texts,
            model=EMBEDDING_MODEL,
            normalize=True
        )

        return result.tolist()


    def embed_query(self, text):
        """
        Convert one user question into a vector.
        """

        result = client.feature_extraction(
            text,
            model=EMBEDDING_MODEL,
            normalize=True
        )

        return result.tolist()