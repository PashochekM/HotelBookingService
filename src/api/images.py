from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.api.dependcencies import ImagesServiceDep
from src.schemas.responses import DataResponse, UploadedImageResponse
from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Изображение отелей"])


@router.post("/images", response_model=DataResponse[UploadedImageResponse])
def upload_image(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    images_service: ImagesServiceDep,
):
    uploaded_image = images_service.upload_image(file)
    # resize_image.delay(image_path)
    background_tasks.add_task(resize_image, str(uploaded_image.path))
    return {"data": {"filename": uploaded_image.filename}}
