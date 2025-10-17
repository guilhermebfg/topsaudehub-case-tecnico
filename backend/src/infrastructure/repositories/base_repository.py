from typing import TypeVar, Generic

from sqlalchemy.orm import Session

from backend.src.exceptions import InvalidSortFieldException

T = TypeVar('T')


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def _apply_sorting(self, stmt, sort_field: str, sort_order: int):
        """
        Apply sorting to a SQLAlchemy statement.

        Args:
            stmt: SQLAlchemy statement
            sort_field: Field name to sort by
            sort_order: Sort order (-1 for DESC, 1 for ASC)

        Returns:
            Statement with sorting applied

        Raises:
            InvalidSortFieldException: If sort_field doesn't exist in model
        """
        order_by = getattr(self.model, sort_field, None)

        if not order_by:
            raise InvalidSortFieldException(sort_field, self.model.__name__)

        if sort_order == -1:
            order_by = order_by.desc()
        elif sort_order == 1:
            order_by = order_by.asc()

        return stmt.order_by(order_by)
