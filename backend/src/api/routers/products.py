from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.src.api.dependencies import get_product_service
from backend.src.application.dtos.product import ProductCreate, ProductEdit, \
    ProductListResponse, \
    ProductQuery, ProductGetResponse
from backend.src.application.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductGetResponse)
def get_product(product_id: int,
                service: ProductService = Depends(get_product_service)):
    """Busca um produto pelo ID."""
    product = service.get(product_id)
    response = ProductGetResponse(cod_retorno=200, mensagem=None, data=product)
    return response


@router.post("", response_model=ProductGetResponse)
def create_product(payload: ProductCreate,
                   service: ProductService = Depends(get_product_service)):
    """Cria um produto."""
    product = service.add(payload)
    response = ProductGetResponse(cod_retorno=200, mensagem=None, data=product)
    return response


@router.put("", response_model=ProductGetResponse)
def update_product(payload: ProductEdit,
                   service: ProductService = Depends(get_product_service)):
    """Atualiza um produto existente."""
    product = service.edit(payload)
    response = ProductGetResponse(cod_retorno=200, mensagem=None, data=product)
    return response


@router.get("", response_model=ProductListResponse)
def list_products(q: Annotated[ProductQuery, Query()],
                  service: ProductService = Depends(get_product_service)):
    """Lista produtos com filtro e paginacao."""
    products = service.list(q)
    response = ProductListResponse(cod_retorno=200, mensagem=None,
                                   data=products)
    return response
