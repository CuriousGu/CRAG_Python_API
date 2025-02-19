from fastapi import APIRouter, status, Request, Depends, HTTPException
from src.api.models import APIResponse
from src.api.models.documents_request import DocumentRequest
from typing import Optional, Dict
from src.api.controllers.controller_document import add_documents
router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("/add_documents", status_code=status.HTTP_200_OK)
async def add_document_route(doc_request: DocumentRequest) -> APIResponse:
    try:
        result = await add_documents(
            doc_request.file_path,
            doc_request.document_content,
            doc_request.collection_name
        )

        return APIResponse(
            status_code=200,
            response=result
        )

    except Exception as e:
        return APIResponse(
            status_code=500,
            status_message=f"Error detalhado: {str(e)}"
        )