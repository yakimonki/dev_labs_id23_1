from fastapi import FastAPI
from app.api import endpoints
from app.db import session

app = FastAPI()

# Подключаем эндпоинты
app.include_router(endpoints.router)

# Инициализация базы данных при старте приложения
@app.on_event("startup")
async def startup_event():
    session.init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
