from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os


def load_pdf(file_bytes: bytes, filename: str):
    """
    Save uploaded PDF temporarily, extract its content,
    attach filename metadata, then delete the temporary file.
    """

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(file_bytes)
            temp_path = tmp.name

        loader = PyPDFLoader(temp_path)

        documents = loader.load()

        for document in documents:
            document.metadata["source_file"] = filename

        return documents

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)