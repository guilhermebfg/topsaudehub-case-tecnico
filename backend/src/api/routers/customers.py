from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.src.api.dependencies import get_customer_service
from backend.src.application.dtos.customer import CustomerListResponse, \
    CustomerQuery, CustomerCreate, \
    CustomerEdit, CustomerGetResponse
from backend.src.application.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=CustomerGetResponse)
def get_customer(customer_id: int,
                 service: CustomerService = Depends(get_customer_service)):
    """Busca um cliente pelo ID."""
    customer = service.get(customer_id)
    response = CustomerGetResponse(cod_retorno=200, mensagem=None,
                                   data=customer)
    return response


@router.get("", response_model=CustomerListResponse)
def list_customers(q: Annotated[CustomerQuery, Query()],
                   service: CustomerService = Depends(get_customer_service)):
    """Lista clientes com filtro e paginacao."""
    customers = service.list(q)
    response = CustomerListResponse(cod_retorno=200, mensagem=None,
                                    data=customers)
    return response


@router.post("", response_model=CustomerGetResponse)
def create_customer(payload: CustomerCreate,
                    service: CustomerService = Depends(get_customer_service)):
    """Cria um novo cliente."""
    customer = service.add(payload)
    response = CustomerGetResponse(cod_retorno=200, mensagem=None,
                                   data=customer)
    return response


@router.put("", response_model=CustomerGetResponse)
def update_customer(payload: CustomerEdit,
                    service: CustomerService = Depends(get_customer_service)):
    """Update an existing customer."""
    customer = service.edit(payload)
    response = CustomerGetResponse(cod_retorno=200, mensagem=None,
                                   data=customer)
    return response
