"""
Centralized logging system for chat sessions.
Each chat session gets its own logger with session_id context.
Provides structured logging with component tags: [ROUTER], [INTENT:name:COMPONENT]
"""

import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class ComponentLoggerAdapter(logging.LoggerAdapter):
    """
    Adapter that adds component tag prefix to all log messages.
    Format: [COMPONENT_TAG] YYYY-MM-DD HH:MM:SS - message
    """
    
    def __init__(self, logger, component_tag: str):
        super().__init__(logger, {})
        self.component_tag = component_tag
    
    def process(self, msg, kwargs):
        """Add component tag prefix and timestamp to message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{self.component_tag}] {timestamp} - {msg}", kwargs


class ChatLogger:
    """Singleton logger manager for chat sessions with structured component logging."""
    
    _instance: Optional['ChatLogger'] = None
    _loggers: dict[str, logging.Logger] = {}
    
    # Logging configuration
    LOG_DIR = Path("logs")
    LOG_LEVEL = logging.INFO
    # Simplified format since we handle timestamp in ComponentLoggerAdapter
    LOG_FORMAT = "%(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize logging system."""
        # Create logs directory if not exists
        self.LOG_DIR.mkdir(exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=self.LOG_LEVEL,
            format=self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )
    
    def get_logger(self, session_id: str) -> logging.Logger:
        """
        Get or create a logger for a specific chat session.
        
        Args:
            session_id: Unique identifier for the chat session
            
        Returns:
            Logger configured for the session
        """
        if session_id not in self._loggers:
            self._loggers[session_id] = self._create_session_logger(session_id)
        
        return self._loggers[session_id]
    
    def get_component_logger(
        self, 
        session_id: str, 
        component: str, 
        intent_name: Optional[str] = None
    ) -> ComponentLoggerAdapter:
        """
        Get a logger with structured component tag for consistent formatting.
        
        Args:
            session_id: Chat session ID
            component: Component type (ROUTER, EXTRACTOR, SERVICE, HANDLER)
            intent_name: Optional intent name for INTENT:name:COMPONENT format
            
        Returns:
            ComponentLoggerAdapter with formatted tag
            
        Examples:
            get_component_logger(sid, 'ROUTER') -> [ROUTER]
            get_component_logger(sid, 'EXTRACTOR', 'worked_hours') -> [INTENT:worked_hours:EXTRACTOR]
        """
        base_logger = self.get_logger(session_id)
        
        if intent_name:
            tag = f"INTENT:{intent_name}:{component}"
        else:
            tag = component
        
        return ComponentLoggerAdapter(base_logger, tag)
    
    def _create_session_logger(self, session_id: str) -> logging.Logger:
        """
        Create a new logger for a chat session.
        
        Args:
            session_id: Unique identifier for the chat session
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"chat.{session_id}")
        logger.setLevel(self.LOG_LEVEL)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.LOG_LEVEL)
        console_formatter = logging.Formatter(
            self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler - one file per session
        log_file = self.LOG_DIR / f"{session_id}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.LOG_LEVEL)
        file_formatter = logging.Formatter(
            self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False
        
        return logger
    
    def log_intent_classification(
        self, 
        session_id: str, 
        user_query: str, 
        classified_intent: str,
        confidence: Optional[float] = None
    ):
        """Log intent classification results."""
        logger = self.get_logger(session_id)
        extra = {'session_id': session_id}
        
        msg = f"Intent classified: '{classified_intent}' for query: '{user_query}'"
        if confidence is not None:
            msg += f" (confidence: {confidence:.2f})"
        
        logger.info(msg, extra=extra)
    
    def log_parameter_extraction(
        self,
        session_id: str,
        intent: str,
        extracted_params: dict
    ):
        """Log extracted parameters for an intent."""
        logger = self.get_logger(session_id)
        extra = {'session_id': session_id}
        
        logger.info(
            f"Parameters extracted for '{intent}': {extracted_params}",
            extra=extra
        )
    
    def log_service_call(
        self,
        session_id: str,
        intent: str,
        service_name: str,
        method: str,
        url: str,
        status_code: Optional[int] = None
    ):
        """Log service API calls."""
        logger = self.get_logger(session_id)
        extra = {'session_id': session_id}
        
        msg = f"Service call [{intent}] {service_name}.{method}: {url}"
        if status_code is not None:
            msg += f" -> {status_code}"
        
        logger.info(msg, extra=extra)
    
    def log_error(
        self,
        session_id: str,
        error_type: str,
        error_msg: str,
        context: Optional[dict] = None
    ):
        """Log errors with context."""
        logger = self.get_logger(session_id)
        extra = {'session_id': session_id}
        
        msg = f"Error [{error_type}]: {error_msg}"
        if context:
            msg += f" | Context: {context}"
        
        logger.error(msg, extra=extra, exc_info=True)
    
    def log_response_generation(
        self,
        session_id: str,
        intent: str,
        response_length: int,
        generation_time: Optional[float] = None
    ):
        """Log response generation metrics."""
        logger = self.get_logger(session_id)
        extra = {'session_id': session_id}
        
        msg = f"Response generated for '{intent}': {response_length} chars"
        if generation_time is not None:
            msg += f" in {generation_time:.2f}s"
        
        logger.info(msg, extra=extra)
    
    def cleanup_old_logs(self, days: int = 30):
        """
        Remove log files older than specified days.
        
        Args:
            days: Number of days to keep logs
        """
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        
        for log_file in self.LOG_DIR.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                logging.info(f"Deleted old log file: {log_file}")


# Singleton instance
chat_logger = ChatLogger()
