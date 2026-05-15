"""Common response schemas used across all API endpoints."""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ErrorDetail(BaseModel):
    """Error response detail."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    status_code: int = Field(..., description="HTTP status code")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper."""
    success: bool = Field(True, description="Operation succeeded")
    data: T = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional success message")


class ErrorResponse(BaseModel):
    """Error response wrapper."""
    success: bool = Field(False, description="Operation failed")
    error: ErrorDetail = Field(..., description="Error details")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class ListResponse(BaseModel, Generic[T]):
    """Generic list response with pagination."""
    success: bool = Field(True, description="Operation succeeded")
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
