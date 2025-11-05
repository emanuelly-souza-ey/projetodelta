from fastapi import FastAPI
from app.api.v1.router import router

app = FastAPI()

app.include_router(router)


@app.get("/")
async def root():
    return{"message": "API funcionando :)"}


# Para rodar a API:
# uvicorn app.main:app --reload