from fastapi import FastAPI
from app.api import endpoints

# Создаем приложение FastAPI
app = FastAPI(
    title="Image Binarization API",
    description="API для превращения изображений в черно-белые",
    version="1.0.0"
)

# Подключаем эндпоинты из файла endpoints.py
app.include_router(endpoints.router)