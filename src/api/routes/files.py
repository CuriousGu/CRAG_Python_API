from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    UploadFile,
    status
)

from src.api.controllers import (
    controller_upload_file,
    controller_list_files,
    controller_list_collections,
    controller_delete_file
)

from src.api.models import FileMetadata, APIResponse


router = APIRouter(tags=["files"], prefix="/files")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_files():
    return APIResponse(
        status_code=status.HTTP_200_OK,
        status_message="The FILES router is working"
    )


@router.get(
    "/list_collections",
    status_code=status.HTTP_200_OK
)
async def list_collections(
    req: Request
):
    try:
        collections = await controller_list_collections(
            vector_store=req.app.vector_store
        )
        return APIResponse(
            status_code=status.HTTP_200_OK,
            status_message="Collections listed successfully",
            response={
                "collections": collections
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/list_files/{collection_name}",
    status_code=status.HTTP_200_OK
)
async def list_files(
    collection_name: str,
    req: Request
):
    try:
        files = await controller_list_files(
            collection_name=collection_name,
            vector_store=req.app.vector_store
        )

        return APIResponse(
            status_code=status.HTTP_200_OK,
            response={
                "files": files
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/upload", status_code=status.HTTP_201_CREATED)
async def upload_files(
    req: Request,
    file: UploadFile = File(...),
) -> APIResponse:
    try:
        _ = await controller_upload_file(
            file=file,
            metadata=FileMetadata(file_name=file.filename),
            vector_store=req.app.vector_store,
        )

        return APIResponse(
            status_code=status.HTTP_201_CREATED,
            status_message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/delete_file/{collection_name}/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_file(
    collection_name: str,
    file_id: str,
    req: Request
):
    try:
        _ = await controller_delete_file(
            collection_name=collection_name,
            file_id=file_id,
            vector_store=req.app.vector_store
        )
        return APIResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            status_message="File deleted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
