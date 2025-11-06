"""
Centralized Azure configuration and client management.
Single source of truth for Azure OpenAI and Azure DevOps credentials.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import instructor
from openai import AzureOpenAI
import requests


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
        response_model: Optional[Any] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ):
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
            return self.instructor_client.chat.completions.create(
                model=self.deployment_name,
                response_model=response_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Use standard OpenAI client
            return self.openai_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )


# Global singleton instance
_azure_config = None


def get_azure_config() -> AzureConfig:
    """Get the global Azure configuration instance."""
    global _azure_config
    if _azure_config is None:
        _azure_config = AzureConfig()
    return _azure_config
