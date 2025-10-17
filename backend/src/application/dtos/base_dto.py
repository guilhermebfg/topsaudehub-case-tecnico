from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Base DTO para todos os DTOs."""
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class BaseResponse(BaseDTO):
    """Base Response para retorno de todos os payloads."""
    cod_retorno: int
    mensagem: Optional[str] = None
