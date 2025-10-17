from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.src.api.dependencies import get_order_service
from backend.src.application.dtos.order import (OrderListResponse, OrderCreate,
                                                OrderEdit, OrderQuery,
                                                OrderGetResponse)
from backend.src.application.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/{order_id}", response_model=OrderGetResponse)
def get_order(order_id: int,
              service: OrderService = Depends(get_order_service)):
    """Busca um pedido pelo ID."""
    order = service.get(order_id)
    response = OrderGetResponse(cod_retorno=200, mensagem=None, data=order)
    return response


@router.get("", response_model=OrderListResponse)
def list_orders(q: Annotated[OrderQuery, Query()],
                service: OrderService = Depends(get_order_service)):
    """Lista pedidos com filtro e paginacao."""
    orders = service.list(q)
    response = OrderListResponse(cod_retorno=200, mensagem=None, data=orders)
    return response


@router.post("", response_model=OrderGetResponse)
def create_order(payload: OrderCreate,
                 service: OrderService = Depends(get_order_service)):
    """Cria um pedido."""
    order = service.add(payload)
    response = OrderGetResponse(cod_retorno=200, mensagem=None, data=order)
    return response


@router.put("", response_model=OrderGetResponse)
def update_order(payload: OrderEdit,
                 service: OrderService = Depends(get_order_service)):
    """Atualiza um pedido existente."""
    order = service.edit(payload)
    response = OrderGetResponse(cod_retorno=200, mensagem=None, data=order)
    return response


@router.put("/{order_id}/charge", response_model=OrderGetResponse)
def charge_order(order_id: int,
                 service: OrderService = Depends(get_order_service)):
    """
    Faz a cobranca do pedido.
    Endpoint apenas para fazer a alteracao do status de pedido ja que estava
    na descricao do case.
    """
    order = service.charge(order_id)
    response = OrderGetResponse(cod_retorno=200, mensagem=None, data=order)
    return response


@router.put("/{order_id}/cancel", response_model=OrderGetResponse)
def cancel_order(order_id: int,
                 service: OrderService = Depends(get_order_service)):
    """Cancela(apenas muda o status) um pedido pelo ID."""
    order = service.cancel(order_id)
    response = OrderGetResponse(cod_retorno=200, mensagem=None, data=order)
    return response
