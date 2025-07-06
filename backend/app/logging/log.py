"""
Structured JSON logging utility for ADOGENT application.
Provides centralized logging with weekly rotation and JSON formatting.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid
import os

from app.config.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
            "service": "adogent-backend",
            "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        # Add extra fields if present
        extra_fields = [
            'user_id', 'request_id', 'session_id', 'endpoint', 'method', 
            'status_code', 'response_time', 'ai_agent', 'groq_model',
            'action', 'details', 'error_context', 'operation', 'table',
            'duration', 'input_tokens', 'output_tokens'
        ]
        
        for field in extra_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class ADOGENTLogger:
    """ADOGENT centralized logging utility."""
    
    def __init__(
        self,
        logger_name: str = "adogent",
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 12,  # Keep 12 weeks of logs
        enable_console: bool = True,
        enable_file: bool = True,
    ):
        self.logger_name = logger_name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        # Ensure log directory is writable
        if not os.access(self.log_dir, os.W_OK):
            print(f"Warning: Log directory {self.log_dir} is not writable")
        
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Set up the logger with handlers and formatters."""
        # Get or create logger
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Create JSON formatter
        json_formatter = JSONFormatter()
        
        # Create console handler with JSON formatting (if enabled)
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(json_formatter)
            self.logger.addHandler(console_handler)
        
        # Create file handlers (if enabled)
        if self.enable_file:
            try:
                # Ensure log directory exists with proper permissions
                os.makedirs(self.log_dir, exist_ok=True)
                
                # Check if log directory is writable
                if not os.access(self.log_dir, os.W_OK):
                    print(f"⚠️ Warning: Log directory {self.log_dir} is not writable")
                    # Try to fix permissions on directory
                    try:
                        os.chmod(self.log_dir, 0o755)
                        print(f"✅ Changed permissions on {self.log_dir} to make it writable")
                    except Exception as e:
                        print(f"❌ Could not change permissions: {e}")
                
                # Create weekly rotating file handler for all logs
                log_file = self.log_dir / f"{self.logger_name}.log"
                
                # Create the log file if it doesn't exist
                if not log_file.exists():
                    try:
                        with open(log_file, 'w') as f:
                            pass  # Just create the file
                        os.chmod(log_file, 0o644)  # Make it readable/writable
                        print(f"✅ Created log file: {log_file}")
                    except Exception as e:
                        print(f"❌ Could not create log file: {e}")
                
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    filename=str(log_file),
                    when='W0',  # Weekly rotation on Monday
                    interval=1,
                    backupCount=self.backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(self.log_level)
                file_handler.setFormatter(json_formatter)
                self.logger.addHandler(file_handler)
                print(f"✅ Added file handler for {log_file}")
                
                # Create error file handler for ERROR and CRITICAL logs
                error_log_file = self.log_dir / f"{self.logger_name}_errors.log"
                
                # Create the error log file if it doesn't exist
                if not error_log_file.exists():
                    try:
                        with open(error_log_file, 'w') as f:
                            pass  # Just create the file
                        os.chmod(error_log_file, 0o644)  # Make it readable/writable
                        print(f"✅ Created error log file: {error_log_file}")
                    except Exception as e:
                        print(f"❌ Could not create error log file: {e}")
                        
                error_handler = logging.handlers.TimedRotatingFileHandler(
                    filename=str(error_log_file),
                    when='W0',  # Weekly rotation on Monday
                    interval=1,
                    backupCount=self.backup_count,
                    encoding='utf-8'
                )
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(json_formatter)
                self.logger.addHandler(error_handler)
                print(f"✅ Added error file handler for {error_log_file}")
                
                # Log successful setup
                print(f"✅ Log files configured: {log_file} and {error_log_file}")
                
            except Exception as e:
                print(f"❌ Error setting up file logging: {e}")
                # Fall back to console only
                if not self.enable_console:
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setLevel(self.log_level)
                    console_handler.setFormatter(json_formatter)
                    self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger
    
    def add_context(self, **context: Any) -> None:
        """Add context to all subsequent log messages."""
        for key, value in context.items():
            setattr(self.logger, key, value)


class LogContext:
    """Context manager for adding temporary logging context."""
    
    def __init__(self, logger: logging.Logger, **context: Any):
        self.logger = logger
        self.context = context
        self.original_values = {}
    
    def __enter__(self):
        # Store original values
        for key in self.context:
            if hasattr(self.logger, key):
                self.original_values[key] = getattr(self.logger, key)
        
        # Set new context
        for key, value in self.context.items():
            setattr(self.logger, key, value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original values
        for key in self.context:
            if key in self.original_values:
                setattr(self.logger, key, self.original_values[key])
            else:
                if hasattr(self.logger, key):
                    delattr(self.logger, key)


# Create global logger instance
_logger_instance = ADOGENTLogger(
    logger_name="adogent",
    log_level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    log_dir=getattr(settings, 'LOG_DIR', 'logs'),
    enable_console=True,  # Keep console for development
    enable_file=True,     # Enable file logging
)

# Export the logger
logger = _logger_instance.get_logger()


# Convenience functions
def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance with optional name."""
    if name:
        return logging.getLogger(f"adogent.{name}")
    return logger


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log API request with structured data."""
    with LogContext(
        logger,
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        response_time=response_time,
        user_id=user_id,
        request_id=request_id,
    ):
        logger.info(f"{method} {endpoint} - {status_code} - {response_time:.3f}s")


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """Log database operation with structured data."""
    with LogContext(
        logger,
        operation=operation,
        table=table,
        duration=duration,
        user_id=user_id,
        session_id=session_id,
    ):
        logger.info(f"DB {operation} on {table} - {duration:.3f}s")


def log_ai_interaction(
    agent_name: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration: float,
    user_id: Optional[str] = None,
) -> None:
    """Log AI agent interaction with structured data."""
    with LogContext(
        logger,
        ai_agent=agent_name,
        groq_model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration=duration,
        user_id=user_id,
    ):
        logger.info(f"AI {agent_name} with {model} - {input_tokens}→{output_tokens} tokens - {duration:.3f}s")


def log_user_action(
    action: str,
    user_id: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log user action with structured data."""
    with LogContext(logger, user_id=user_id, action=action, details=details):
        logger.info(f"User {user_id} performed {action}")


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> None:
    """Log error with structured data and context."""
    with LogContext(logger, user_id=user_id, error_context=context):
        logger.error(f"Error: {str(error)}", exc_info=True)