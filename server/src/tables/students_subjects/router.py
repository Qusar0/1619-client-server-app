from fastapi import APIRouter, HTTPException
from src.tables.students_subjects.dao import StudentSubjectDAO
from src.tables.students_subjects.schemas import SStudentSubjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.session_maker import TransactionSessionDep


router = APIRouter(prefix='/student-subjects', tags=['Работа с оценками студентов'])

@router.put('/update/{student_id}')
async def update_student_rates(student_id: int, student_subjects: list[SStudentSubjectUpdate], session: AsyncSession = TransactionSessionDep):
    check = await StudentSubjectDAO.update_many_by_student_id(student_id=student_id, student_subjects=student_subjects, session=session)
    if not check:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении оценок студента!")
    return {'message': f'Оценки студента успешно обновлены!'}
