from typing_extensions import Annotated
from typing import Annotated, Any, Dict, List, Optional, Sequence, Tuple, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BigInteger, \
    select, update, delete, func, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import DeclarativeBase, registry


bigint = Annotated[int, 64]
T = TypeVar("T")


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            bigint: BigInteger,
        },
    )

    @classmethod
    async def get_by_id(
        cls: Type[T], session: AsyncSession, model_id: int | str
    ) -> T | None:
        row = await session.execute(select(cls).where(cls.id == model_id))
        return row.scalar_one_or_none()

    @classmethod
    async def get_by_other(
        cls: Type[T],
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None
    ) -> T | None:
        match = select(cls)
        if extra_where_clauses:
            match = match.where(and_(*extra_where_clauses))

        result = await session.execute(match)
        return result.scalar()

    @classmethod
    async def get_all(
        cls: Type[T],
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None
    ) -> Sequence[T]:
        match = select(cls)

        if extra_where_clauses:
            match = match.where(and_(*extra_where_clauses))

        result = await session.execute(match)
        return result.scalars().all()

    @classmethod
    async def create(
        cls: Type[T],
        session: AsyncSession,
        params: List[Dict[str, Any]] | Dict[str, Any],
    ) -> T:
        stmt = pg_insert(cls).values(params).on_conflict_do_nothing().returning(cls)
        result = await session.execute(stmt)

        return result.scalar()

    @classmethod
    async def update(
        cls: Type[T], session: AsyncSession, model_id: int | str, **kwargs: Any
    ) -> T:
        result = await session.execute(
            update(cls).where(cls.id == model_id).values(**kwargs).returning(cls)
        )
        return result.scalar()

    @classmethod
    async def updateall(
        cls: Type[T],
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None,
        **kwargs: Any
    ) -> T:
        match = (
            update(cls)
            .values(**kwargs)
        )

        if extra_where_clauses:
            match = match.where(and_(*extra_where_clauses))

        result = await session.execute(match.returning(cls))

        return result.scalar()

    @classmethod
    async def delete(cls, session: AsyncSession, model_id: int | str | None = None):
        match = delete(cls)
        if model_id:
            match = match.where(cls.id == model_id)

        await session.execute(match)

    @classmethod
    async def delete_by_other(
        cls,
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None
    ):
        match = delete(cls)

        if extra_where_clauses:
            match = match.where(*extra_where_clauses)

        await session.execute(match)

    @classmethod
    async def deletemany(
        cls,
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None
    ) -> None:
        match = delete(cls)

        if extra_where_clauses:
            match = match.where(and_(*extra_where_clauses))

        await session.execute(match)

    @classmethod
    async def count(
        cls,
        session: AsyncSession,
        extra_where_clauses: List[Any] | None = None
    ):
        match = select(func.count(cls.id))
        if extra_where_clauses:
            match = match.where(and_(*extra_where_clauses))
        return (await session.execute(match)).scalar()
