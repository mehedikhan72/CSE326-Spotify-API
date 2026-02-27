from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class SuccessMessage(BaseModel):
    message: str


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
