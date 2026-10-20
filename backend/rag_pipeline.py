
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter

from file_loader import load_pdf
from vector_store import get_vector_store


load_dotenv()

# ---------------------------------------------------------
# Google Gemini configuration
# ---------------------------------------------------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not configured.")

client = genai.Client(api_key=GOOGLE_API_KEY)


# ---------------------------------------------------------
# Process document
# ---------------------------------------------------------

def process_document(
    file_bytes: bytes,
    filename: str,
    session_id: str
):
    """Load PDF, split text, embed chunks, and store vectors."""

    documents = load_pdf(file_bytes, filename)

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
    """Retrieve relevant document chunks."""

    vector_store = get_vector_store(session_id)

    return vector_store.similarity_search(query, k=k)


# ---------------------------------------------------------
# Generate streaming response using Gemini
# ---------------------------------------------------------

def query_rag_stream(
    query: str,
    session_id: str
):
    """Retrieve context and stream a Gemini response."""

    try:
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

            page = document.metadata.get("page", 0)
            page_number = page + 1

            context_parts.append(
                f"Source: {filename}\n"
                f"Page: {page_number}\n\n"
                f"{document.page_content}"
            )

        context = "\n\n".join(context_parts)

        system_instruction = (
            "You are DocuMind AI, an intelligent document assistant. "
            "Answer questions using only the supplied document context. "
            "Do not invent facts or use outside knowledge. "
            "If the answer is absent from the context, say that the "
            "information is not available in the uploaded document. "
            "Keep answers clear and concise."
        )

        prompt = (
            f"DOCUMENT CONTEXT:\n\n{context}\n\n"
            f"USER QUESTION:\n\n{query}"
        )

        stream = client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=400,
                temperature=0.1
            )
        )

        received_text = False

        for chunk in stream:
            text = getattr(chunk, "text", None)

            if text:
                received_text = True
                yield {
                    "type": "token",
                    "content": text
                }

        if not received_text:
            yield {
                "type": "error",
                "message": (
                    "Gemini returned no answer text. "
                    "Check the model and API response."
                )
            }
            return

        # -------------------------------------------------
        # Send source citations after the answer
        # -------------------------------------------------

        sources = []
        seen = set()

        for document in documents:
            filename = document.metadata.get(
                "source_file",
                "Unknown document"
            )

            page_number = document.metadata.get("page", 0) + 1
            source_key = (filename, page_number)

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

        yield {"type": "done"}

    except Exception as e:
        print(f"DocuMind RAG error: {type(e).__name__}: {e}")

        yield {
            "type": "error",
            "message": (
                f"Unable to generate an answer: "
                f"{type(e).__name__}: {e}"
            )
        }
