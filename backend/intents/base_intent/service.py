"""
Base service for querying data from external sources.
All intent services should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter, Retry

from backend.config import get_azure_config
from backend.config.logging import chat_logger
from .models import BaseQueryParams, BaseResponse


class BaseService(ABC):
    """
    Abstract base class for intent services.
    Handles data retrieval from Azure DevOps or other external sources.
    
    Provides common error handling, timeout, and retry logic.
    
    Each intent must implement:
    - query_data(): Method to query and retrieve data
    """
    
    # Default configurations (can be overridden by subclasses)
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_RETRY_TOTAL = 3
    DEFAULT_RETRY_BACKOFF_FACTOR = 0.5
    
    def __init__(self, session_id: Optional[str] = None, intent_name: Optional[str] = None):
        """
        Initialize the service with shared Azure config and HTTP session.
        
        Args:
            session_id: Optional chat session ID for logging
            intent_name: Optional intent name for structured logging
        """
        self.azure_config = get_azure_config()
        self.session_id = session_id
        self.intent_name = intent_name
        
        # Use structured component logger if session_id provided
        if session_id:
            self.logger = chat_logger.get_component_logger(
                session_id=session_id,
                component='SERVICE',
                intent_name=intent_name
            )
        else:
            self.logger = None
        
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        Subclasses can override to customize retry behavior.
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.DEFAULT_RETRY_TOTAL,
            backoff_factor=self.DEFAULT_RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def make_request(
        self,
        method: str,
        url: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with error handling and timeout.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)
            **kwargs: Additional arguments for requests (headers, json, data, etc.)
            
        Returns:
            Response object
            
        Raises:
            requests.exceptions.Timeout: If request times out
            requests.exceptions.HTTPError: If HTTP error occurs
            requests.exceptions.RequestException: For other request errors
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        
        if self.logger:
            self.logger.info(f"Making {method} request to {url} (timeout: {timeout}s)")
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()
            
            if self.logger:
                self.logger.info(f"Request successful: {method} {url} -> {response.status_code}")
            
            return response
            
        except requests.exceptions.Timeout as e:
            if self.logger:
                self.logger.error(f"Request timeout: {method} {url} after {timeout}s", exc_info=True)
            raise TimeoutError(f"Request to {url} timed out after {timeout}s") from e
        
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            if self.logger:
                self.logger.error(f"HTTP error {status_code}: {method} {url}", exc_info=True)
            raise Exception(
                f"HTTP error {status_code} for {url}: {str(e)}"
            ) from e
        
        except requests.exceptions.RequestException as e:
            if self.logger:
                self.logger.error(f"Request failed: {method} {url} - {str(e)}", exc_info=True)
            raise Exception(f"Request failed for {url}: {str(e)}") from e
    
    @abstractmethod
    async def query_data(self, params: BaseQueryParams) -> BaseResponse:
        """
        Query data based on extracted parameters.
        
        Args:
            params: Extracted query parameters (BaseQueryParams subclass)
            
        Returns:
            Service response (BaseResponse subclass)
            
        Example implementation:
            async def query_data(self, params: WorkedHoursQuery) -> WorkedHoursResponse:
                # Build WIQL query
                wiql_query = self._build_wiql_query(params)
                
                # Execute API request
                url = self.azure_config.get_devops_url() + "/_apis/wit/wiql?api-version=7.1"
                response = requests.post(
                    url,
                    headers=self.azure_config.get_devops_headers(),
                    json={"query": wiql_query}
                )
                
                # Process response
                data = response.json()
                return self._process_response(data, params)
        """
        pass
    
    def _build_wiql_query(self, params: BaseQueryParams) -> str:
        """
        Helper method to build WIQL queries for Azure DevOps.
        Subclasses can override this for specific query construction.
        
        Args:
            params: Query parameters
            
        Returns:
            WIQL query string
        """
        raise NotImplementedError("Subclass must implement _build_wiql_query if using WIQL")
    
    def _get_project_id(self, params: BaseQueryParams) -> str:
        """
        Helper method to get project ID.
        Uses provided project_id or falls back to default from config.
        
        Args:
            params: Query parameters
            
        Returns:
            Azure DevOps project ID
        """
        if hasattr(params, 'project_id') and params.project_id:
            return params.project_id
        return self.azure_config.devops_project_id
