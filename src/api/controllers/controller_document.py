from src.infrastructure.database.chromadb.conector import ChromaDB
from src.services.docmuent_extration.extractor import DocumentFileReader
from typing import List, Dict, Optional


async def add_documents(
    db: ChromaDB,
    file_path: str,
    document_content: str,
    collection_name: str
) -> Dict:
    
    reader = DocumentFileReader(file_path, document_content)
    result = await db.add_documents(
        documents=reader.documents,
        collection_name=collection_name,
        metadatas=reader.metadata,
        ids=reader.ids
    )
    return result

async def query_documents(
    db: ChromaDB,
    query_text: str,
    collection_name: str,
    n_results: int = 5,
    where: Optional[dict] = None
):
    result = await db.query_documents(
        query_text=query_text,
        collection_name=collection_name,
        n_results=n_results,
        where=where) 
    return result

async def delete_documents(
    db: ChromaDB,
    ids: List[str],
    collection_name: str
):
    result = await db.delete_documents(
        ids=ids,
        collection_name=collection_name
    )
    return result