from pydantic import BaseModel

class DocumentRequest(BaseModel):
    file_path: str
    document_content: str
    collection_name: str