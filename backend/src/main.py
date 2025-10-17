import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from backend.src.api.routers import products, customers, orders, health
from backend.src.exceptions import NotFoundException, BusinessRuleException, \
    DuplicateEntryException
from backend.src.infrastructure.database import engine
from backend.src.infrastructure.models import Base
from backend.src.settings import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
request_locks = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def idempotency_lock_middleware(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

    key = request.headers.get("Idempotency-Key")
    if not key:
        return await call_next(request)

    lock = request_locks.setdefault(key, asyncio.Lock())

    if lock.locked():
        raise HTTPException(status_code=409,
                            detail="Request already in progress")

    async with lock:
        try:
            response = await call_next(request)
        finally:
            request_locks.pop(key, None)
        return response


def _payload(code: int, msg: str):
    return {"cod_retorno": code, "mensagem": msg, "data": None}


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content=_payload(404, exc.detail))


@app.exception_handler(DuplicateEntryException)
async def duplicate_entry_handler(request: Request,
                                  exc: DuplicateEntryException):
    return JSONResponse(status_code=409, content=_payload(409, exc.detail))


@app.exception_handler(BusinessRuleException)
async def business_rule_handler(request: Request, exc: BusinessRuleException):
    return JSONResponse(status_code=422, content=_payload(422, exc.detail))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
                        content=_payload(exc.status_code, exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422,
                        content=_payload(422, "Validation error"))


app.include_router(products.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(health.router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
