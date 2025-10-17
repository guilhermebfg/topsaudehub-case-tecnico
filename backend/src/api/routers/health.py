from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.src.exceptions import BusinessRuleException, \
    DuplicateEntryException
from backend.src.infrastructure.database import get_db
from backend.src.settings import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica se a conexao da API e do banco estao ok.
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        raise Exception(f"unhealthy: {str(e)}")

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.app_env,
        "version": settings.app_version,
        "services": {
            "database": db_status
        }
    }


@router.get("/business-rule-exception")
def business_rule_exception():
    """Retorna uma exception de regra de negocios apenas para testes."""
    raise BusinessRuleException("Product Invalid SKU")


@router.get("/request-validation-error")
def request_validation_error():
    """Retorna uma exception de validacao de requisicao apenas para testes."""
    raise RequestValidationError("Product Invalid SKU")



@router.get("/duplicate-entry-error")
def duplicate_entry_error():
    """Retorna uma exception de validacao de requisicao apenas para testes."""
    raise DuplicateEntryException("Test")
