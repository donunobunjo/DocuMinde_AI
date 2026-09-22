import os
import json
import uuid

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag_pipeline import (
    process_document,
    query_rag_stream
)


# =========================================================
# Application
# =========================================================

app = FastAPI(
    title="DocuMind AI API",
    description="RAG-powered document intelligence API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Request models
# =========================================================

class ChatRequest(BaseModel):

    session_id: str
    query: str


# =========================================================
# Health check
# =========================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "application": "DocuMind AI",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# =========================================================
# Upload
# =========================================================

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    # Create unique session
    session_id = uuid.uuid4().hex

    try:

        result = process_document(
            file_bytes=contents,
            filename=file.filename,
            session_id=session_id
        )

        return {
            "message": "Document processed successfully.",
            "session_id": session_id,
            "filename": result["filename"],
            "pages": result["pages"],
            "chunks": result["chunks"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


# =========================================================
# Streaming chat
# =========================================================

@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest
):

    if not request.session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required."
        )

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    def event_generator():

        for event in query_rag_stream(
            query=request.query,
            session_id=request.session_id
        ):

            yield (
                f"data: {json.dumps(event)}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )