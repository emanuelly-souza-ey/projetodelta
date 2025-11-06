from fastapi import FastAPI
from .api.v1.router import router

app = FastAPI()

app.include_router(router, prefix="/api/v1", tags=["v1"])

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

# uvicorn backend.main:app --reload