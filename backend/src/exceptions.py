from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=f"{entity} with id {entity_id} not found")


class DuplicateEntryException(HTTPException):
    def __init__(self, entity: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT,
                         detail=f"{entity} already registered")


class BusinessRuleException(HTTPException):
    def __init__(self, detail: str = "Business rule violation"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                         detail=detail)


class InvalidSortFieldException(HTTPException):
    def __init__(self, field: str, model: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Invalid sort field '{field}' for {model}")
