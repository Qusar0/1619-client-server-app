from src.dao.base import BaseDAO
from src.tables.students_subjects.models import StudentSubject
from src.tables.students_subjects.schemas import SStudentSubjectUpdate
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from src.tables.departments.schemas import DepartmentModel


class StudentSubjectDAO(BaseDAO[StudentSubject]):
    model = StudentSubject

    @classmethod
    async def update_many_by_student_id(cls, student_id: int, student_subjects: list[SStudentSubjectUpdate], session: AsyncSession,):
        for student_subject in student_subjects:
            query = select(cls.model).where(cls.model.student_id == student_id).where(cls.model.subject_id == student_subject.subject_id)
            result = await session.execute(query)
            student_subject_data = result.scalar_one_or_none()
            
            for key, value in student_subject.model_dump(exclude_unset=True).items():
                setattr(student_subject_data, key, value)
        
            session.add(student_subject_data)

        return True