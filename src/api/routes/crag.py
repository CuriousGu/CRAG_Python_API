from fastapi import APIRouter, HTTPException, status, Request, Depends

from src.api.models import APIResponse, APIRequest
from src.api.controllers import Guardrail
from src.api.controllers.crag import contr_new_message

router = APIRouter(
    prefix="/crag",
    tags=["CRAG"],
    dependencies=[
        # Depends(Guardrail())
    ]
)


@router.post("/new_message", status_code=status.HTTP_200_OK)
async def new_message(api_request: APIRequest, req: Request) -> APIResponse:
    try:
        response = await contr_new_message(
            api_request.message,
            req.app.crag,
            req.app.llm,
            req.app.vector_store
        )
        return APIResponse(
            success=True,
            message="Message created successfully",
            data=response
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
