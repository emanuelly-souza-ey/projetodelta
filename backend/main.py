from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api.v1.router import router

load_dotenv()

app = FastAPI(
    title="Delta API",
    version="1.0.0"
)

# CORS para permitir o front React
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API v1
app.include_router(router, prefix="/api/v1", tags=["v1"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agil.IA API"}