from fastapi import APIRouter
from src.tables.students_subjects.dao import StudentSubjectDAO
from src.tables.students_subjects.schemas import SStudentSubjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.session_maker import AsyncSessionDep, AsyncTransactionSessionDep
from src.tables.departments.schemas import DepartmentModel


router = APIRouter(prefix='/student-subjects', tags=['Работа с оценками студентов'])

@router.put('/update/{student_id}')
async def update_student_rates(student_id: int, student_subjects: list[SStudentSubjectUpdate], session: AsyncSession = AsyncTransactionSessionDep):
    check = await StudentSubjectDAO.update_many_by_student_id(student_id=student_id, student_subjects=student_subjects, session=session)
    if check:
        return {'message': f'Оценки студента успешно обновлены!'}
    return {"message": "Ошибка при обновлении оценок студента!"}
