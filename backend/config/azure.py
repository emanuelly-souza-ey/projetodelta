"""
Centralized Azure configuration and client management.
Single source of truth for Azure OpenAI and Azure DevOps credentials.
"""

import os
from typing import Optional, Dict, Any, TypeVar, cast
from dotenv import load_dotenv
import instructor
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
import requests


T = TypeVar('T')


class AzureConfig:
    """
    Centralized Azure configuration manager.
    Manages credentials and provides singleton client instances.
    """
    
    _instance = None
    _openai_client = None
    _instructor_client = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        if self._initialized:
            return
            
        load_dotenv()
        
        # Azure OpenAI credentials
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01")
        
        # Azure DevOps credentials
        self.devops_url = os.getenv("AZURE_DEVOPS_URL")
        self.devops_token = os.getenv("AZURE_DEVOPS_TOKEN")
        self.devops_project_id = os.getenv("AZURE_PROJECT_ID", "e4005fd0-7b95-4391-8486-c4b21c935b2e")
        
        # Validate required credentials
        self._validate_credentials()
        
        self._initialized = True
    
    def _validate_credentials(self):
        """Validate that all required credentials are present."""
        if not self.openai_endpoint or not self.openai_key:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables."
            )
        
        if not self.devops_url or not self.devops_token:
            raise ValueError(
                "Azure DevOps credentials not found. "
                "Set AZURE_DEVOPS_URL and AZURE_DEVOPS_TOKEN environment variables."
            )
    
    @property
    def openai_client(self) -> AzureOpenAI:
        """
        Get or create the Azure OpenAI client.
        Singleton instance shared across all uses.
        """
        if self._openai_client is None:
            # Type narrowing: we validated these in __init__
            assert self.openai_endpoint is not None, "OpenAI endpoint must be set"
            assert self.openai_key is not None, "OpenAI key must be set"
            
            self._openai_client = AzureOpenAI(
                azure_endpoint=self.openai_endpoint,
                api_key=self.openai_key,
                api_version=self.api_version
            )
        return self._openai_client
    
    @property
    def instructor_client(self):
        """
        Get or create the instructor-patched Azure OpenAI client.
        Singleton instance for structured outputs.
        """
        if self._instructor_client is None:
            self._instructor_client = instructor.from_openai(self.openai_client)
        return self._instructor_client
    
    def get_devops_headers(self) -> Dict[str, str]:
        """Get headers for Azure DevOps API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.devops_token}",
        }
    
    def get_devops_url(self, project_id: Optional[str] = None) -> str:
        """
        Get Azure DevOps base URL with optional project.
        
        Args:
            project_id: Optional project ID (uses default if not provided)
            
        Returns:
            Base URL for Azure DevOps API
        """
        pid = project_id or self.devops_project_id
        return f"{self.devops_url}/{pid}"
    
    def create_chat_completion(
        self,
        messages: list,
        response_model: Optional[type[T]] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> T | ChatCompletion:
        """
        Create a chat completion with consistent settings.
        
        Args:
            messages: List of message dictionaries
            response_model: Optional Pydantic model for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Completion response (structured if response_model provided)
        """
        if response_model:
            # Use instructor for structured output
            # Type checker can't infer instructor's dynamic return type, so we cast
            result = self.instructor_client.chat.completions.create(
                model=self.deployment_name,
                response_model=response_model,  # type: ignore[arg-type]
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return cast(T, result)
        else:
            # Use standard OpenAI client
            return self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
    
    def validate_openai_connection(self) -> Dict[str, Any]:
        """
        Validate Azure OpenAI connection with a test completion.
        
        Returns:
            Dict with status and details about the connection
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Connection successful' in Spanish."}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            return {
                "status": "success",
                "message": "Azure OpenAI connection is working",
                "endpoint": self.openai_endpoint,
                "deployment": self.deployment_name,
                "test_response": response.choices[0].message.content,
                "model": response.model
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Azure OpenAI connection failed: {str(e)}",
                "endpoint": self.openai_endpoint,
                "deployment": self.deployment_name,
                "error_type": type(e).__name__
            }
    
    def validate_devops_connection(self) -> Dict[str, Any]:
        """
        Validate Azure DevOps connection by fetching project information.
        
        Returns:
            Dict with status and details about the connection
        """
        try:
            # Test the connection by getting project info
            url = f"{self.devops_url}/_apis/projects/{self.devops_project_id}?api-version=7.0"
            headers = self.get_devops_headers()
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            project_data = response.json()
            
            return {
                "status": "success",
                "message": "Azure DevOps connection is working",
                "devops_url": self.devops_url,
                "project_id": self.devops_project_id,
                "project_name": project_data.get("name", "Unknown"),
                "project_state": project_data.get("state", "Unknown")
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Azure DevOps connection failed: {str(e)}",
                "devops_url": self.devops_url,
                "project_id": self.devops_project_id,
                "error_type": type(e).__name__
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
                "devops_url": self.devops_url,
                "project_id": self.devops_project_id,
                "error_type": type(e).__name__
            }


# Global singleton instance
_azure_config = None


def get_azure_config() -> AzureConfig:
    """Get the global Azure configuration instance."""
    global _azure_config
    if _azure_config is None:
        _azure_config = AzureConfig()
    return _azure_config
