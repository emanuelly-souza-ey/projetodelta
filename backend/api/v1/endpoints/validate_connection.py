"""
Connection validation endpoints for Azure services.
Provides health check endpoints for Azure OpenAI and Azure DevOps.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.config.azure import get_azure_config

router = APIRouter()


@router.get("/openai", response_model=Dict[str, Any])
async def validate_openai_connection() -> Dict[str, Any]:
    """
    Validate Azure OpenAI connection.
    
    Tests the connection by making a simple chat completion request.
    
    Returns:
        Dict containing connection status and details
        
    Raises:
        HTTPException: If validation completely fails
    """
    try:
        azure_config = get_azure_config()
        result = azure_config.validate_openai_connection()
        
        # If the validation returned an error status, we still return it
        # but with appropriate HTTP status code
        if result.get("status") == "error":
            raise HTTPException(status_code=503, detail=result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Unexpected error during validation: {str(e)}",
                "error_type": type(e).__name__
            }
        )


@router.get("/devops", response_model=Dict[str, Any])
async def validate_devops_connection() -> Dict[str, Any]:
    """
    Validate Azure DevOps connection.
    
    Tests the connection by fetching project information.
    
    Returns:
        Dict containing connection status and details
        
    Raises:
        HTTPException: If validation completely fails
    """
    try:
        azure_config = get_azure_config()
        result = azure_config.validate_devops_connection()
        
        # If the validation returned an error status, raise HTTP error
        if result.get("status") == "error":
            raise HTTPException(status_code=503, detail=result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Unexpected error during validation: {str(e)}",
                "error_type": type(e).__name__
            }
        )


@router.get("/all", response_model=Dict[str, Any])
async def validate_all_connections() -> Dict[str, Any]:
    """
    Validate all Azure connections at once.
    
    Tests both Azure OpenAI and Azure DevOps connections.
    
    Returns:
        Dict containing status for both services
    """
    azure_config = get_azure_config()
    
    openai_result = azure_config.validate_openai_connection()
    devops_result = azure_config.validate_devops_connection()
    
    # Determine overall status
    all_successful = (
        openai_result.get("status") == "success" and 
        devops_result.get("status") == "success"
    )
    
    return {
        "overall_status": "success" if all_successful else "partial_failure",
        "openai": openai_result,
        "devops": devops_result
    }
