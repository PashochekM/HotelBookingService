import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, BackgroundTasks
from PIL import Image, UnidentifiedImageError

from src.config import BASE_DIR
from src.exceptions import InvalidImageError
from src.tasks.tasks import resize_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["Изображение отелей"])

IMAGES_DIR = BASE_DIR / "src" / "static" / "images"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@router.post("/images")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    content_type = file.content_type or ""
    suffix = Path(file.filename or "").suffix.lower()
    if content_type not in ALLOWED_IMAGE_TYPES or suffix not in ALLOWED_IMAGE_SUFFIXES:
        logger.warning("image_upload_rejected reason=unsupported_type filename=%s content_type=%s", file.filename, content_type)
        raise InvalidImageError("Unsupported image type")

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_name = f"{uuid4().hex}{suffix}"
    image_path = IMAGES_DIR / image_name

    written_size = 0
    try:
        with open(image_path, "wb+") as image_file:
            while chunk := file.file.read(1024 * 1024):
                written_size += len(chunk)
                if written_size > MAX_IMAGE_SIZE:
                    logger.warning("image_upload_rejected reason=too_large filename=%s size=%s", file.filename, written_size)
                    raise InvalidImageError("Image is too large")
                image_file.write(chunk)
    except InvalidImageError:
        image_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        image_path.unlink(missing_ok=True)
        logger.exception("image_save_failed filename=%s", file.filename)
        raise InvalidImageError("Could not save image") from exc
    finally:
        file.file.close()

    try:
        with Image.open(image_path) as image:
            image.verify()
    except (OSError, UnidentifiedImageError) as exc:
        image_path.unlink(missing_ok=True)
        logger.warning("image_upload_rejected reason=invalid_image filename=%s content_type=%s", file.filename, content_type)
        raise InvalidImageError("Uploaded file is not a valid image") from exc

    # resize_image.delay(image_path)
    background_tasks.add_task(resize_image, str(image_path))
    logger.info(
        "image_uploaded original_filename=%s stored_filename=%s content_type=%s size=%s",
        file.filename,
        image_name,
        content_type,
        written_size,
    )
    return {"status": "ok", "filename": image_name}
