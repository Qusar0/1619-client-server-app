from fastapi import APIRouter
from src.tables.students.dao import StudentDAO
from src.tables.students.schemas import SStudentAdd, SStudentSelect
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.session_maker import SessionDep, TransactionSessionDep

from src.tables.groups.dao import GroupDAO
from src.dao.balanced_function import balanced_function
from pydantic import create_model

router = APIRouter(prefix='/students', tags=['Работа со студентами'])

@router.get('/', summary='Получить всех студентов')
async def get_students(session: AsyncSession = SessionDep) -> list[SStudentSelect]:
    return await StudentDAO.find_full_data_students(session)

@router.post('/add/', summary='Добавить студента')
async def add_student(department_id: int, student: SStudentAdd, session: AsyncSession = TransactionSessionDep):
    DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))
    department = DepartmentModel(department_id=department_id)

    current_groups = await GroupDAO.find_all(session=session, filters=department)
    if len(current_groups) == 0:
        group_id = await GroupDAO.add_group(department_id=department_id, session=session)
    else:
        group_id = current_groups[0].id
    check = await StudentDAO.add_student(department_id=department_id, group_id=group_id, student=student, session=session)
    if check:
        await balanced_function(department_id=department_id, session=session)
        return {"message": "Студент успешно добавлен!"}
    return {"message": "Студент не был добавлен!"}

@router.delete('/{id}', summary='Удалить студента по ID')
async def delete_student(id: int, session: AsyncSession = TransactionSessionDep):
    student = await StudentDAO.find_one_or_none_by_id(data_id=id, session=session)
    if student:
        group = await GroupDAO.find_one_or_none_by_id(data_id=student.group_id, session=session)
        if group:
            department_id = group.department_id
            await StudentDAO.delete_one_by_id(data_id=id, session=session)
            await balanced_function(department_id=department_id, session=session)
            return {"message": "Студент успешно удалён!"}
        else:
            return {"message": "Группа студента не найдена!"}
    return {"message": "Студент с указанным ID не найден!"}

@router.get('/{department_id}')
async def students_in_department(department_id: int, session: AsyncSession = SessionDep):
    return await StudentDAO.students_by_department_id(department_id=department_id, session=session)
