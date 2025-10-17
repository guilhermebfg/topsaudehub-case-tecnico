from datetime import datetime
from typing import Optional, Sequence

from pydantic import Field

from backend.src.application.dtos.base_dto import BaseDTO, BaseResponse
from backend.src.application.dtos.base_query import BaseQuery
from backend.src.application.dtos.customer import CustomerGet
from backend.src.application.dtos.page import Page
from backend.src.application.dtos.product import ProductGet
from backend.src.infrastructure.models.orders import OrderStatus


class OrderItemCreate(BaseDTO):
    """DTO de criacao item de um pedido seguindo a ordem cria -> edita ->
    busca."""
    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")


class OrderItemEdit(OrderItemCreate):
    """DTO de edicao item de um pedido seguindo a ordem cria -> edita ->
    busca."""
    id: Optional[int] = Field(None, gt=0, description="Item ID (if existing)")
    unit_price: float = Field(..., gt=0, description="Unit price")


class OrderCreate(BaseDTO):
    """DTO criacao de pedido seguindo a ordem cria -> edita -> busca."""
    customer_id: int = Field(..., gt=0, description="Customer ID")
    items: Sequence[OrderItemCreate] = Field(..., min_length=1,
                                             description="Order items (at "
                                                         "least one required)")


class OrderEdit(OrderCreate):
    """DTO de edicao de um pedido seguindo a ordem cria -> edita ->
    busca."""
    id: int = Field(..., gt=0, description="Order ID")
    items: Sequence[OrderItemEdit] = Field(..., min_length=1)


class OrderItemGet(BaseDTO):
    """DTO de busca de um pedido seguindo a ordem cria -> edita ->
    busca."""
    id: int = Field(..., gt=0, description="Order item ID")
    product: ProductGet
    unit_price: float = Field(..., gt=0, description="Unit price")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")
    line_total: float = Field(..., gt=0, description="Line total")


class OrderGet(OrderEdit):
    """DTO de busca de um pedido seguindo a ordem cria -> edita -> busca."""
    created_at: datetime
    items: Sequence[OrderItemGet]
    customer: CustomerGet
    status: OrderStatus = Field(..., description="Order status")
    total_amount: float = Field(..., gt=0, description="Total amount")


class OrderGetResponse(BaseResponse):
    """DTO de resposta de busca de um pedido seguindo a ordem cria -> edita ->
    busca."""
    cod_retorno: int
    mensagem: Optional[str] = None
    data: Optional[OrderGet] = None


class OrderListResponse(BaseDTO):
    """DTO de resposta de listagem de pedidos."""
    cod_retorno: int
    mensagem: Optional[str] = None
    data: Optional[Page[OrderGet]] = None


class OrderQuery(BaseQuery):
    """DTO de listagem de pedidos com paginacao e sort etc."""
    id: Optional[int] = Field(None, gt=0, description="Filter by order ID")
    customer: Optional[str] = Field(None, min_length=1, max_length=120,
                                    description="Filter by customer name, "
                                                "e-mail or document")
    status: Optional[OrderStatus] = Field(None,
                                          description="Filter by order status")
    total_amount: Optional[float] = Field(None,
                                          description="Filter by minimum "
                                                      "total amount")
    created_min: Optional[datetime] = Field(None,
                                            description="Filter by minimum "
                                                        "creation date")
