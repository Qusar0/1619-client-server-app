from fastapi import APIRouter, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Union

from src.tables.instructors.dao import InstructorDAO
from src.tables.students.dao import StudentDAO
from src.tables.instructors.schemas import SInstructorSelect, SInstructorAdd, SInstructorUpdate
from src.tables.departments.schemas import DepartmentModel

from src.dao.session_maker import AsyncSessionDep, AsyncTransactionSessionDep, SyncTransactionSessionDep
from src.dao.group_balancer import balance_groups


router = APIRouter(prefix='/instructors', tags=['Работа с кураторами'])

@router.get('/', summary='Получить всех кураторов')
async def get_instructors(session: AsyncSession = AsyncSessionDep) -> list[SInstructorSelect]:
    return await InstructorDAO.find_full_data_instructors(session)

@router.get('/{id}', summary='Получить куратора по ID')
async def get_instructor_by_id(instructor_id: int, session: AsyncSession = AsyncSessionDep) -> Union[SInstructorSelect, dict]:
    result = await InstructorDAO.find_full_data_instructor_by_id(session=session, instructor_id=instructor_id)
    if result is None:
        return {'message': f'Куратор с ID {instructor_id} не найден!'}
    return result

@router.post('/add/', summary='Добавить нового куратора')
async def add_instructor(
    instructor: SInstructorAdd,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    check = await InstructorDAO.add(session=async_session, values=instructor)
    if check:
        background_tasks.add_task(balance_groups, instructor.department_id, sync_session)
        return {"message": "Куратор успешно добавлен!", "instructor": instructor}
    else:
        return {"message": "Ошибка при добавлении куратора!"}
    
@router.put('/update/{id}', summary='Обновить данные куратора по ID')
async def update_instructor(
    id: int,
    instructor_data: SInstructorUpdate,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=async_session)
    if instructor is None:
        return {'message': f'Куратор с ID {id} не найден!'}
    
    instructor_department_id = instructor.department_id
    if instructor_data.department_id and instructor_department_id != instructor_data.department_id:
        department = DepartmentModel(department_id=instructor_department_id)
        instructors = await InstructorDAO.async_find_all(session=async_session, filters=department)
        if len(instructors) == 1:
            return {"message": "Невозможно перевести последнего куратора с кафедры на которой числятся студенты!"}

    check = await InstructorDAO.update_one_by_id(session=async_session, data_id=id, values=instructor_data)
    if check:
        if instructor_data.department_id:
            background_tasks.add_task(balance_groups, instructor_data.department_id, sync_session)
        if instructor_department_id != instructor_data.department_id:
            background_tasks.add_task(balance_groups, instructor_department_id, sync_session)
        return {"message": "Данные куратора успешно обновлены!"}
    else:
        return {"message": "Ошибка при обновлении данных куратора!"}

@router.delete('/delete/{id}', summary='Удалить куратора по ID')
async def delete_instructor(
    id: int,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=async_session)
    if instructor:
        department = DepartmentModel(department_id=instructor.department_id)

        students = await StudentDAO.async_students_by_department_id(department_id=instructor.department_id, session=async_session)
        instructors = await InstructorDAO.async_find_all(session=async_session, filters=department)

        if len(instructors) <= 1 and students:
            return {"message": "Нельзя удалить последнего преподавателя, так как на кафедре числятся студенты!"}

        await InstructorDAO.async_delete_one_by_id(data_id=id, session=async_session)
        background_tasks.add_task(balance_groups, instructor.department_id, sync_session)
        return {"message": "Данные куратора успешно удалены!"}

    return {"message": "Ошибка при удалении данных куратора!"}
