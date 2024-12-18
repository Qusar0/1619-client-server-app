from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.database import Base

T = TypeVar("T", bound=Base)

class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        try:
            return await session.get(cls.model, data_id)
        except SQLAlchemyError as e:
            print(f"Error occurred: {e}")
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            return record
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def find_all(cls, session: AsyncSession, filters: BaseModel | None = None):
        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        new_instances = [cls.model(**values) for values in values_list]
        session.add_all(new_instances)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instances
    
    @classmethod
    async def update_one_by_id(cls, session: AsyncSession, data_id: int, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        try:
            record = await session.get(cls.model, data_id)
            for key, value in values_dict.items():
                setattr(record, key, value)
            await session.flush()
            return data_id
        except SQLAlchemyError as e:
            print(e)
            raise e
        
    @classmethod
    async def update_many(cls, session: AsyncSession, filter_criteria: BaseModel, values: BaseModel):
        filter_dict = filter_criteria.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        try:
            query = (
                update(cls.model)
                .filter_by(**filter_dict)
                .values(**values_dict)
            )
            result = await session.execute(query)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            print(f"Error in mass update: {e}")
            raise

    @classmethod
    async def delete_one_by_id(cls, data_id: int, session: AsyncSession):
        try:
            data = await session.get(cls.model, data_id)
            if data:
                await session.delete(data)
                await session.flush()
        except SQLAlchemyError as e:
            print(f"Error occurred: {e}")
            raise

    @classmethod
    async def delete_many(cls, session: AsyncSession, filters: BaseModel | None):
        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
            query = delete(cls.model).filter_by(**filter_dict)
        else:
            query = delete(cls.model)
        try:
            result = await session.execute(query)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            print(f"Error occurred: {e}")
            raise