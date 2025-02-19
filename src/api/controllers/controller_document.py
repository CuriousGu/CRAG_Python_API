from src.infrastructure.database.chromadb.conector import ChromaDB
from src.services.docmuent_extration.extractor import DocumentFileReader
from typing import List, Dict


async def add_documents(
    file_path: str,
    document_content: str,
    collection_name: str
) -> Dict:
    db = ChromaDB()
    
    reader = DocumentFileReader(file_path, document_content)
    result = await db.add_documents(
        documents=reader.documents,
        collection_name=collection_name,
        metadatas=reader.metadata,
        ids=reader.ids
    )
    return result
