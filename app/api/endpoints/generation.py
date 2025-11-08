from fastapi import APIRouter, HTTPException, status
from app.modals.schemas import GenerationRequest, TaskResponse
from app.services.content_service import ContentService
from app.services.task_service import TaskService

router = APIRouter()
content_service = ContentService()
task_service = TaskService()


@router.post("/generate/brand-kit", response_model=TaskResponse)
async def generate_brand_kit(request: GenerationRequest):
    try:
        task_id = await content_service.generate_brand_kit(request.dict())
        task_data = task_service.get_task(task_id)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

        return TaskResponse(
            task_id=task_id,
            status=task_data["status"],
            created_at=task_data["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/generate/social-media", response_model=TaskResponse)
async def generate_social_media(request: GenerationRequest):
    try:
        task_id = await content_service.generate_social_media(request.dict())
        task_data = task_service.get_task(task_id)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

        return TaskResponse(
            task_id=task_id,
            status=task_data["status"],
            created_at=task_data["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/generate/website", response_model=TaskResponse)
async def generate_website_content(request: GenerationRequest):
    try:
        task_id = await content_service.generate_website_content(request.dict())
        task_data = task_service.get_task(task_id)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

        return TaskResponse(
            task_id=task_id,
            status=task_data["status"],
            created_at=task_data["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    task_data = task_service.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(**task_data)
