import re
from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator, EmailStr

from backend.src.application.dtos.base_dto import BaseDTO, BaseResponse
from backend.src.application.dtos.base_query import BaseQuery
from backend.src.application.dtos.page import Page


class CustomerCreate(BaseDTO):
    """DTO para criacao de cliente seguindo a ordem cria -> edita -> busca."""
    name: str = Field(..., min_length=3, max_length=120,
                      description="Customer full name")
    email: EmailStr = Field(..., description="Customer email address")
    document: str = Field(..., min_length=11, max_length=14,
                          description="Customer document (CPF/CNPJ)")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida que o nome contém apenas letras."""
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', v):
            raise ValueError("Name must contain only letters and spaces")
        return v.strip()

    @field_validator('document')
    @classmethod
    def validate_document(cls, v: str) -> str:
        """Valida tamanho do documento para garantir CPF ou CNPJ."""
        clean_doc = re.sub(r'\D', '', v)

        if len(clean_doc) not in [11, 14]:
            raise ValueError(
                "Document must be 11 digits (CPF) or 14 digits (CNPJ)")

        if len(set(clean_doc)) == 1:
            raise ValueError("Invalid document: all digits are the same")

        return clean_doc


class CustomerEdit(CustomerCreate):
    """DTO para edicao de cliente seguindo a ordem cria -> edita -> busca."""
    id: int = Field(..., gt=0, description="Customer ID")


class CustomerGet(CustomerEdit):
    """DTO para busca de cliente seguindo a ordem cria -> edita -> busca."""
    created_at: datetime


class CustomerQuery(BaseQuery):
    """Query para busca de clientes."""
    id: Optional[int] = Field(None, gt=0, description="Filter by customer ID")
    name: Optional[str] = Field(None, min_length=1, max_length=120,
                                description="Filter by customer name")
    email: Optional[str] = Field(None, min_length=3,
                                 description="Filter by customer email")
    document: Optional[str] = Field(None, min_length=11, max_length=14,
                                    description="Filter by customer document")
    created_min: Optional[datetime] = Field(None,
                                            description="Filter by minimum "
                                                        "creation date")


class CustomerGetResponse(BaseResponse):
    """DTO para resposta de busca de cliente."""
    data: Optional[CustomerGet] = None


class CustomerListResponse(BaseResponse):
    """DTO para resposta de listagem de clientes."""
    data: Optional[Page[CustomerGet]] = None
