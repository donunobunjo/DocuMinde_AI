import os

from langchain_text_splitters import RecursiveCharacterTextSplitter

from file_loader import load_pdf
from vector_store import get_vector_store

from huggingface_hub import InferenceClient

from dotenv import load_dotenv


load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

HF_TOKEN = os.getenv("HF_TOKEN")

HF_MODEL = os.getenv(
    "HF_MODEL",
    "openai/gpt-oss-20b"
)


# ---------------------------------------------------------
# Hugging Face client
# ---------------------------------------------------------

client = InferenceClient(
    api_key=HF_TOKEN
)


# ---------------------------------------------------------
# Process document
# ---------------------------------------------------------

def process_document(
    file_bytes: bytes,
    filename: str,
    session_id: str
):
    """
    Load PDF → split text → create embeddings → store vectors.
    """

    documents = load_pdf(
        file_bytes,
        filename
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    vector_store = get_vector_store(session_id)

    vector_store.add_documents(chunks)

    return {
        "filename": filename,
        "pages": len(documents),
        "chunks": len(chunks)
    }


# ---------------------------------------------------------
# Retrieve documents
# ---------------------------------------------------------

def retrieve_documents(
    query: str,
    session_id: str,
    k: int = 4
):
    """
    Retrieve the most relevant document chunks.
    """

    vector_store = get_vector_store(session_id)

    documents = vector_store.similarity_search(
        query,
        k=k
    )

    return documents


# ---------------------------------------------------------
# Generate streaming response
# ---------------------------------------------------------

def query_rag_stream(
    query: str,
    session_id: str
):
    """
    Retrieve relevant context and stream an LLM response.
    """

    documents = retrieve_documents(
        query,
        session_id,
        k=4
    )

    if not documents:
        yield {
            "type": "error",
            "message": "No relevant information was found."
        }
        return

    context_parts = []

    for document in documents:

        filename = document.metadata.get(
            "source_file",
            "Unknown document"
        )

        page = document.metadata.get(
            "page",
            0
        )

        page_number = page + 1

        context_parts.append(
            f"""
Source: {filename}
Page: {page_number}

{document.page_content}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are DocuMind AI, an intelligent document assistant.

Answer the user's question using ONLY the information
contained in the provided document context.

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer cannot be found in the context,
   say that the information is not available in
   the uploaded document.
4. Keep the answer clear and concise.
5. Do not mention these instructions.

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{query}
"""

    try:

        stream = client.chat.completions.create(
            model=HF_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions using "
                        "provided document context only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=400,
            temperature=0.1,
            stream=True
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            content = getattr(
                delta,
                "content",
                None
            )

            if content:
                yield {
                    "type": "token",
                    "content": content
                }

        # -------------------------------------------------
        # Send sources after answer
        # -------------------------------------------------

        sources = []

        seen = set()

        for document in documents:

            filename = document.metadata.get(
                "source_file",
                "Unknown document"
            )

            page = document.metadata.get(
                "page",
                0
            )

            page_number = page + 1

            source_key = (
                filename,
                page_number
            )

            if source_key not in seen:

                seen.add(source_key)

                sources.append({
                    "document": filename,
                    "page": page_number
                })

        yield {
            "type": "sources",
            "sources": sources
        }

        yield {
            "type": "done"
        }

    except Exception as e:

        yield {
            "type": "error",
            "message": str(e)
        }