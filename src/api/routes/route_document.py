from fastapi import APIRouter, status, Request, Depends, HTTPException
from src.api.models import APIResponse
from src.api.models.documents_request import AddDocumentRequest, QueryDocumentRequest, ListDocumentsRequest, ListCollectionsRequest, DeleteDocumentRequest
from typing import Optional, Dict
from src.api.controllers.controller_document import add_documents, query_documents, delete_documents, list_collections, list_documents

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("/add_documents", status_code=status.HTTP_200_OK)
async def add_document_route(doc_request: AddDocumentRequest, req: Request) -> APIResponse:
    try:
        result = await add_documents(
            req.app.vectordb,
            doc_request.file_path,
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
    
@router.post("/query_documents", status_code=status.HTTP_200_OK)
async def query_document_route(doc_request: QueryDocumentRequest, req: Request) -> APIResponse:
    try:
        result = await query_documents(
            req.app.vectordb,
            doc_request.query_text,
            doc_request.collection_name,
            doc_request.n_results,
            doc_request.where
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

@router.get("/list_collections", status_code=status.HTTP_200_OK)
async def list_collections_route(req: Request):
    try:
        result = await list_collections(req.app.vectordb)
        return {
            "status_code": 200,
            "response": result  # Retorna diretamente a lista de nomes das coleções
        }
    except Exception as e:
        return {
            "status_code": 500,
            "status_message": f"Erro detalhado: {str(e)}"
        }
    
@router.post("/list_documents", status_code=status.HTTP_200_OK)
async def list_documents_route(doc_request: ListDocumentsRequest, req: Request) -> APIResponse:
    try:
        result = await list_documents(
            req.app.vectordb,
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

@router.delete("/delete_documents", status_code=status.HTTP_200_OK)
async def delete_document_route(doc_request: DeleteDocumentRequest, req: Request) -> APIResponse:
    try:
        result = await delete_documents(
            req.app.vectordb,
            doc_request.ids,
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