
import os
import math

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 384

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is not configured."
    )

client = genai.Client(api_key=GOOGLE_API_KEY)


def normalize_vector(vector):
    """Normalize a vector for cosine-similarity retrieval."""

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def embed_texts(texts):
    """Generate embeddings for one or more text inputs."""

    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    return [
        normalize_vector(embedding.values)
        for embedding in response.embeddings
    ]


class GeminiEmbeddings:
    """Gemini-backed embeddings compatible with Chroma."""

    def embed_documents(self, texts):
        return embed_texts(texts)

    def embed_query(self, text):
        return embed_texts([text])[0]
