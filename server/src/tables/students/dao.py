from src.dao.base import BaseDAO
from src.tables.students.models import Student
from src.tables.students.schemas import SStudentAdd
from src.tables.groups.models import Group
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from src.tables.instructors.dao import InstructorDAO
from pydantic import create_model

class StudentDAO(BaseDAO[Student]):
    model = Student

    @classmethod
    async def find_full_data_students(cls, session: AsyncSession) -> dict:
        query = select(cls.model).options(
            joinedload(cls.model.group)
            .joinedload(Group.department)
        )
        
        result = await session.execute(query)
        students = result.unique().scalars().all()

        if not students:
            return None

        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'group': student.group.name if student.group else None,
                'department': student.group.department.name if student.group and student.group.department else None,
            })

        return students_data
    
    @classmethod
    async def students_by_department_id(cls, department_id: int, session: AsyncSession):
        try:
            print(f"department_id {department_id}")
            query = (
                select(cls.model)
                .join(cls.model.group)
                .join(Group.department)
                .where(Group.department_id == department_id)
            )

            result = await session.execute(query)
            
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Error occurred while counting rows: {e}")
            raise

    @classmethod
    async def add_student(cls, department_id: int, group_id: int, student: SStudentAdd, session: AsyncSession):
        DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))
        department = DepartmentModel(department_id=department_id)

        instructors = await InstructorDAO.find_all(session=session, filters=department)
        if not instructors:
            return False
        
        values_dict = student.model_dump(exclude_unset=True)
        new_student = cls.model(**values_dict)
        new_student.group_id = group_id
        session.add(new_student)
        try:
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
