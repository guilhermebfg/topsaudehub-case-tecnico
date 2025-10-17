from dataclasses import dataclass
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """DTO base de paginacao para ter o total de itens."""
    items: Sequence[T]
    total: int
