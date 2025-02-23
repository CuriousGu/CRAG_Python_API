from pydantic import BaseModel
from typing import Optional, List, Dict

class AddDocumentRequest(BaseModel):
    file_path: str
    tags_documnets: str
    collection_name: str

class QueryDocumentRequest(BaseModel):
    query_text: str
    collection_name: str
    n_results: Optional[int] = 5
    where: Optional[Dict] = None

class DeleteDocumentRequest(BaseModel):
    ids: List[str]
    collection_name: str

class ListDocumentsRequest(BaseModel):   
    collection_name: str

class ListCollectionsRequest(BaseModel):
    pass