import chromadb
from chromadb.config import Settings
import openai
from flask import current_app

# Initialize a persistent Chroma client.
client = chromadb.Client(
    Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db")
)

# Get or create a collection for documents.
collection = client.get_or_create_collection("documents")

def get_embedding(text: str) -> list:
    """
    Uses OpenAI's embeddings API to generate a vector representation.
    Ensure that OPENAI_API_KEY is set in your environment/config.
    """
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response["data"][0]["embedding"]

def index_document(tenant_id: int, document_id: str, document_text: str) -> dict:
    """
    Computes the embedding for a document and adds it to the ChromaDB collection.
    Each document is tagged with its tenant_id.
    """
    try:
        embedding = get_embedding(document_text)
        collection.add(
            ids=[document_id],
            embeddings=[embedding],
            documents=[document_text],
            metadatas=[{"tenant_id": tenant_id}]
        )
        return {"status": "success", "message": "Document indexed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_document(tenant_id: int, query_text: str, n_results: int = 3) -> dict:
    """
    Computes the embedding for the query and performs a similarity search on documents
    belonging to the given tenant.
    """
    try:
        query_embedding = get_embedding(query_text)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"tenant_id": tenant_id}
        )
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}
