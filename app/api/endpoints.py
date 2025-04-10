from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image
from app.services.binarization import binarize_image

router = APIRouter()


# Описываем, как выглядит запрос от пользователя
class ImageRequest(BaseModel):
    image: str  # Картинка в формате base64
    algorithm: str  # Какой алгоритм использовать


# Описываем, как выглядит ответ
class ImageResponse(BaseModel):
    binarized_image: str  # Результат в base64


# Эндпоинт для обработки запроса
@router.post("/binary_image", response_model=ImageResponse)
async def binary_image(request: ImageRequest):
    try:
        # Преобразуем строку base64 обратно в картинку
        image_data = base64.b64decode(request.image)
        image = Image.open(BytesIO(image_data))

        # Применяем бинаризацию
        binarized = binarize_image(image, request.algorithm)

        # Преобразуем результат обратно в base64
        buffered = BytesIO()
        binarized.save(buffered, format="PNG")
        binarized_base64 = base64.b64encode(buffered.getvalue()).decode()

        return {"binarized_image": binarized_base64}
    except Exception as e:
        # Если что-то пошло не так, сообщаем об ошибке
        raise HTTPException(status_code=400, detail=str(e))