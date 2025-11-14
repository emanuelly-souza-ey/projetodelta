# Allow to test each intent individually
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.config.azure import get_azure_config

router = APIRouter()
