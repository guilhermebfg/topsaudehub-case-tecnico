from pydantic import BaseModel, Field


class BaseQuery(BaseModel):
    """Base query para fazer paginacao e ordenacao."""
    first: int = Field(0, ge=0, description="Offset for pagination")
    rows: int = Field(10, ge=5, le=50, description="Number of rows per page")
    sort_field: str = Field("id", description="Field to sort by")
    sort_order: int = Field(1, ge=-1, le=1,
                            description="Sort order: -1 for DESC, 1 for ASC, "
                                        "0 for no sorting")
