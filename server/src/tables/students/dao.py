from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from src.dao.base import BaseDAO
from src.tables.departments.schemas import DepartmentModel
from src.tables.students.models import Student
from src.tables.students.schemas import SStudentAdd, SStudentUpdate, SStudentSelect
from src.tables.groups.models import Group
from src.tables.students_subjects.models import StudentSubject
from src.tables.groups.dao import GroupDAO
from src.tables.students_subjects.schemas import SStudentSubjectSelect, SStudentSubjectAdd
from src.tables.students_subjects.dao import StudentSubjectDAO
from src.tables.subjects.models import Subject

class StudentDAO(BaseDAO[Student]):
    model = Student

    @classmethod
    async def find_full_data_students(cls, session: AsyncSession) -> list[SStudentSelect]:
        query = select(cls.model).options(
            joinedload(cls.model.group)
            .joinedload(Group.department)
        )
        
        result = await session.execute(query)
        students = result.unique().scalars().all()

        if not students:
            return []

        students_data = []
        for student in students:
            student = SStudentSelect(
                id=student.id,
                first_name=student.first_name,
                last_name=student.last_name,
                group=student.group.name,
                department_id=student.group.department.id,
                department=student.group.department.name
            )
            students_data.append(student)

        return students_data
    
    @classmethod
    async def find_full_data_student_by_id(cls, student_id: int, session: AsyncSession) -> SStudentSelect:
        query = select(cls.model).options(
            joinedload(cls.model.group).joinedload(Group.department),
            joinedload(cls.model.studentSubject).joinedload(StudentSubject.subject),
            joinedload(cls.model.studentSubject).joinedload(StudentSubject.rate)
        ).where(cls.model.id == student_id)
        
        result = await session.execute(query)
        student = result.unique().scalar_one_or_none()
        if student is None:
            return

        subjects = []
        if student.studentSubject:
            subjects = [SStudentSubjectSelect(
                        subject_id=subj.subject.id,
                        subject_name=subj.subject.name,
                        rate_id=subj.rate.id,
                        rate=subj.rate.name)
                    for subj in student.studentSubject] 

        student_data = SStudentSelect(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            group=student.group.name,
            department_id=student.group.department.id,
            department=student.group.department.name,
            subjects=subjects
        )

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
            raise

    @classmethod
    async def add_student(cls, group_id: int, student: SStudentAdd, session: AsyncSession):        
        values_dict = student.model_dump(exclude_unset=True)
        new_student = cls.model(**values_dict)
        new_student.group_id = group_id
        session.add(new_student)
        try:
            await session.commit()
            return new_student.id
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        
    @classmethod
    async def add_student_subjects(cls, student_id: int, department_id: int, session: AsyncSession):
        query = select(Subject.id).where(Subject.department_id == department_id)

        result = await session.execute(query)

        subjects_ids = result.scalars().all()

        student_subjects = [
            SStudentSubjectAdd(
                student_id=student_id,
                subject_id=subject_id,
                rate_id=1
            )
            for subject_id in subjects_ids
        ]

        await StudentSubjectDAO.add_many(session=session, instances=student_subjects)
        
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
            raise e
