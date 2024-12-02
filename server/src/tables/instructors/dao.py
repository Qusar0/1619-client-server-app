from src.tables.dao.base import BaseDAO
from src.tables.instructors.models import Instructor
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from src.database import async_session_maker
from sqlalchemy import insert, update, delete


class InstructorDAO(BaseDAO):
    model = Instructor

    @classmethod
    async def find_full_data_instructors(cls):
        async with async_session_maker() as session:
            query = select(cls.model).options(
                joinedload(cls.model.department),
                joinedload(cls.model.groups)
            )
            result = await session.execute(query)
            instructors = result.unique().scalars().all()

            if not instructors:
                return None

            instructors_data = []
            for instructor in instructors:
                instructor_data = instructor.to_dict()
                instructor_data['department'] = instructor.department.name if instructor.department else None
                instructor_data['groups'] = [group.name for group in instructor.groups] if instructor.groups else []
                instructors_data.append(instructor_data)

            return instructors_data

    @classmethod
    async def find_full_data_instructor_by_id(cls, instructor_id):
        async with async_session_maker() as session:
            query = select(cls.model).options(
                joinedload(cls.model.department),
                joinedload(cls.model.groups)
            ).filter_by(id=instructor_id)

            result = await session.execute(query)
            instructor_info = result.unique().scalar_one_or_none()

            if not instructor_info:
                return None

            instructor_data = instructor_info.to_dict()
            instructor_data['department'] = instructor_info.department.name if instructor_info.department else None
            instructor_data['groups'] = [group.name for group in instructor_info.groups] if instructor_info.groups else []

            return instructor_data
        
    @classmethod
    async def add_instructor(cls, instructor_data: dict):
        async with async_session_maker() as session:
            async with session.begin():
                query = insert(cls.model).values(**instructor_data)
                result = await session.execute(query)
                await session.commit()
                return result.inserted_primary_key[0]
            
    @classmethod
    async def delete_instructor_by_id(cls, instructor_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=instructor_id)
                result = await session.execute(query)
                instructor_to_delete = result.scalar_one_or_none()

                if not instructor_to_delete:
                    return None
                
                await session.execute(
                    delete(cls.model).filter_by(id=instructor_id)
                )

                await session.commit()
                return instructor_id