from src.dao.base import BaseDAO
from src.tables.instructors.models import Instructor
from src.tables.instructors.schemas import SInstructorSelect
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class InstructorDAO(BaseDAO[Instructor]):
    model = Instructor

    @classmethod
    async def find_full_data_instructors(cls, session: AsyncSession):
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
            instructor_data = SInstructorSelect(
                id=instructor.id,
                first_name=instructor.first_name,
                last_name=instructor.last_name,
                department_id=instructor.department.id,
                department=instructor.department.name,
                groups=[group.name for group in instructor.groups] if instructor.groups else []
            )
            instructors_data.append(instructor_data)

        return instructors_data

    @classmethod
    async def find_full_data_instructor_by_id(cls, session: AsyncSession, instructor_id: int):
        query = select(cls.model).options(
            joinedload(cls.model.department),
            joinedload(cls.model.groups)
        ).filter_by(id=instructor_id)

        result = await session.execute(query)
        instructor_info = result.unique().scalar_one_or_none()

        if not instructor_info:
            return None

        instructor_data = instructor_info.to_dict()
        instructor_data['department'] = instructor_info.department.name
        instructor_data['groups'] = [group.name for group in instructor_info.groups] if instructor_info.groups else []

        return instructor_data