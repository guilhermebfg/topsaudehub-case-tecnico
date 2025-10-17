import re
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from backend.src.application.dtos.base_dto import BaseDTO, BaseResponse
from backend.src.application.dtos.base_query import BaseQuery
from backend.src.application.dtos.page import Page


class ProductCreate(BaseDTO):
    """DTO de criacao de produto seguindo a ordem cria -> edita ->
    busca."""
    name: str = Field(..., min_length=3, max_length=120,
                      description="Product name")
    sku: str = Field(..., min_length=3, max_length=50,
                     description="Stock Keeping Unit")
    price: float = Field(..., gt=0,
                         description="Product price (must be positive)")
    stock_qty: int = Field(..., ge=0,
                           description="Stock quantity (must be non-negative)")
    is_active: bool = Field(True, description="Whether the product is active")

    @field_validator('name', 'sku')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Valida que o nome nao veio vazio ou so espacos"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Z]{3}-\d{3}", v):
            raise ValueError("SKU invalid format")
        return v


class ProductEdit(ProductCreate):
    id: int = Field(..., gt=0, description="Product ID")


class ProductGet(ProductEdit):
    created_at: datetime


class ProductGetResponse(BaseResponse):
    data: Optional[ProductGet] = None


class ProductListResponse(BaseResponse):
    data: Optional[Page[ProductGet]] = None


class ProductQuery(BaseQuery):
    id: Optional[int] = Field(None, gt=0, description="Filter by product ID")
    name: Optional[str] = Field(None, min_length=1, max_length=120,
                                description="Filter by product name")
    sku: Optional[str] = Field(None, min_length=1, max_length=50,
                               description="Filter by SKU")
    price: Optional[float] = Field(None, gt=0,
                                   description="Filter by minimum price")
    stock_qty: Optional[int] = Field(None, ge=0,
                                     description="Filter by minimum stock "
                                                 "quantity")
    is_active: Optional[bool] = Field(None,
                                      description="Filter by active status")
    created_min: Optional[datetime] = Field(None,
                                            description="Filter by minimum "
                                                        "creation date")
