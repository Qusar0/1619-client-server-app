from src.dao.base import BaseDAO
from src.tables.students.models import Student
from src.tables.students.schemas import SStudentAdd, SStudentUpdate
from src.tables.groups.models import Group
from src.tables.groups.dao import GroupDAO
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from src.tables.departments.schemas import DepartmentModel


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
    async def find_full_data_student_by_id(cls, student_id: int, session: AsyncSession) -> dict:
        query = select(cls.model).options(
            joinedload(cls.model.group)
            .joinedload(Group.department)
        ).where(cls.model.id == student_id)
        
        result = await session.execute(query)
        student = result.scalar_one_or_none()
        if student is None:
            return

        student_data = {
                'id': student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'group': student.group.name,
                'department_id': student.group.department_id,
                'department': student.group.department.name
            }

        return student_data
    
    @classmethod
    async def students_by_department_id(cls, department_id: int, session: AsyncSession):
        try:
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
    async def add_student(cls, group_id: int, student: SStudentAdd, session: AsyncSession):        
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
        
    @classmethod
    async def update_student(cls, student_id: int, updated_data: SStudentUpdate, session: AsyncSession) -> bool:
        try:
            query = select(cls.model).where(cls.model.id == student_id)
            result = await session.execute(query)
            student = result.scalar_one_or_none()
            
            if student is None:
                raise ValueError(f"Студент с ID {student_id} не найден")
            
            for key, value in updated_data.model_dump(exclude_unset=True).items():
                setattr(student, key, value)
            
            if updated_data.department_id:
                depatment = DepartmentModel(department_id=updated_data.department_id)
                groups = await GroupDAO.find_all(session=session, filters=depatment)
                if not len(groups):
                    new_group = GroupDAO.add_group(department_id=updated_data.department_id)

                    session.add(new_group)
                    await session.flush()
                    student.group_id = new_group.id
                else:
                    student.group_id = groups[0].id
            
            session.add(student)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"Ошибка при обновлении студента: {e}")
            raise e
