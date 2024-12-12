from fastapi import APIRouter, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Union

from src.tables.students.dao import StudentDAO
from src.tables.instructors.dao import InstructorDAO
from src.tables.students.schemas import SStudentAdd, SStudentSelect, SStudentUpdate
from src.tables.groups.dao import GroupDAO
from src.tables.departments.schemas import DepartmentModel

from src.dao.session_maker import AsyncSessionDep, AsyncTransactionSessionDep, SyncTransactionSessionDep
from src.dao.group_balancer import balance_groups


router = APIRouter(prefix='/students', tags=['Работа со студентами'])

@router.get('/', summary='Получить всех студентов')
async def get_students(session: AsyncSession = AsyncSessionDep) -> list[SStudentSelect]:
    return await StudentDAO.find_full_data_students(session)

@router.get('/{id}', summary='Получить студента по ID')
async def get_student_by_id(student_id: int, session: AsyncSession = AsyncSessionDep) -> Union[SStudentSelect, dict]:
    result = await StudentDAO.find_full_data_student_by_id(student_id=student_id, session=session)
    if result is None:
        return {'message': f'Студент с ID {student_id} не найден!'}
    return result

@router.post('/add/', summary='Добавить студента')
async def add_student(
    department_id: int,
    student: SStudentAdd,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    department = DepartmentModel(department_id=department_id)

    instructors = await InstructorDAO.async_find_all(session=async_session, filters=department)
    if not instructors:
        return {"message": "Невозможно добавить студента на кафедру без куратора!"}

    current_groups = await GroupDAO.async_find_all(session=async_session, filters=department)
    if not len(current_groups):
        group_id = await GroupDAO.async_add_group(department_id=department_id, session=async_session)
    else:
        group_id = current_groups[0].id

    student_id = await StudentDAO.add_student(group_id=group_id, student=student, session=async_session)
    if student_id:
        await StudentDAO.add_student_subjects(student_id=student_id, department_id=department_id, session=async_session)
        background_tasks.add_task(balance_groups, department_id, sync_session)
        return {"message": "Студент успешно добавлен!"}
    return {"message": "Студент не был добавлен!"}

@router.put('/update/{id}', summary='Обновить данные студента по ID')
async def update_student(
    id: int,
    student_data: SStudentUpdate,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    student = await StudentDAO.find_full_data_student_by_id(student_id=id, session=async_session)
    if student is None:
        return {"message": f"Не удалось найти студента с ID {id}!"}
    
    student_department_id = student.get('department_id')

    if student_data.department_id and student_department_id != student_data.department_id:
        department = DepartmentModel(department_id=student_data.department_id)
        instructors = await InstructorDAO.async_find_all(session=async_session, filters=department)
        if len(instructors) < 1:
            return {"message": "Невозможно перевести студента на кафедру без кураторов!"}

    check = await StudentDAO.update_student(student_id=student.get('id'), updated_data=student_data, session=async_session)
    if check:
        if student_data.department_id:
            background_tasks.add_task(balance_groups, student_department_id, sync_session)
        if student_department_id != student_data.department_id:
            background_tasks.add_task(balance_groups, student_data.department_id, sync_session)
        return {"message": "Данные студента успешно обновлены!"}
    return {"message": "Ошибка при обновлении данных студента!"}


@router.delete('/{id}', summary='Удалить студента по ID')
async def delete_student(
    id: int,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = AsyncTransactionSessionDep,
    sync_session: Session = SyncTransactionSessionDep
) -> dict:
    student = await StudentDAO.find_one_or_none_by_id(data_id=id, session=async_session)
    if student:
        group = await GroupDAO.find_one_or_none_by_id(data_id=student.group_id, session=async_session)
        if group:
            await StudentDAO.async_delete_one_by_id(data_id=id, session=async_session)
            background_tasks.add_task(balance_groups, group.department_id, sync_session)
            return {"message": "Студент успешно удалён!"}
        else:
            return {"message": "Группа студента не найдена!"}
    return {"message": "Студент с указанным ID не найден!"}
