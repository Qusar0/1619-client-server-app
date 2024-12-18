from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
import json

from src.tables.students.dao import StudentDAO
from src.tables.instructors.dao import InstructorDAO
from src.tables.students.schemas import SStudentAdd, SStudentSelect, SStudentUpdate
from src.tables.groups.dao import GroupDAO
from src.tables.departments.schemas import DepartmentModel

from src.dao.session_maker import SessionDep, TransactionSessionDep
from src.dao.group_balancer import balance_groups
from src.connection_manager import manager


router = APIRouter(prefix='/students', tags=['Работа со студентами'])

@router.get('/', summary='Получить всех студентов')
async def get_students(session: AsyncSession = SessionDep) -> Optional[list[SStudentSelect]]:
    return await StudentDAO.find_full_data_students(session)

@router.get('/{id}', summary='Получить студента по ID')
async def get_student_by_id(student_id: int, session: AsyncSession = SessionDep) -> Union[SStudentSelect, dict]:
    result = await StudentDAO.find_full_data_student_by_id(student_id=student_id, session=session)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Студент с ID {student_id} не найден!")
    return result

@router.post('/add/', summary='Добавить студента')
async def add_student(
    department_id: int,
    student: SStudentAdd,
    background_tasks: BackgroundTasks,
    session: AsyncSession = TransactionSessionDep,
) -> dict:
    department = DepartmentModel(department_id=department_id)

    instructors = await InstructorDAO.find_all(session=session, filters=department)
    if not instructors:
        raise HTTPException(status_code=400, detail="Невозможно добавить студента на кафедру без куратора!")

    current_groups = await GroupDAO.find_all(session=session, filters=department)
    if not len(current_groups):
        group_id = await GroupDAO.add_group(department_id=department_id, session=session)
    else:
        group_id = current_groups[0].id

    student_id = await StudentDAO.add_student(group_id=group_id, student=student, session=session)
    if not student_id:
        raise HTTPException(status_code=500, detail="Не удалось добавить студента!")

    await StudentDAO.add_student_subjects(student_id=student_id, department_id=department_id, session=session)
    background_tasks.add_task(balance_groups, department_id, session)
    students = await get_students(session)
    await manager.broadcast(json.dumps({
            "category": "students",
            "data": [student.model_dump() for student in students]
    }))
    return {"message": "Студент успешно добавлен!"}

@router.put('/update/{id}', summary='Обновить данные студента по ID')
async def update_student(
    id: int,
    student_data: SStudentUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = TransactionSessionDep,
) -> dict:
    student = await StudentDAO.find_full_data_student_by_id(student_id=id, session=session)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Не удалось найти студента с ID {id}!")

    student_department_id = student.get('department_id')

    if student_data.department_id and student_department_id != student_data.department_id:
        department = DepartmentModel(department_id=student_data.department_id)
        instructors = await InstructorDAO.find_all(session=session, filters=department)
        if len(instructors) < 1:
            raise HTTPException(status_code=400, detail="Невозможно перевести студента на кафедру без кураторов!")

    check = await StudentDAO.update_student(student_id=student.get('id'), updated_data=student_data, session=session)
    if not check:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении данных студента!")

    if student_data.department_id:
        background_tasks.add_task(balance_groups, student_department_id, session)
    if student_department_id != student_data.department_id:
        background_tasks.add_task(balance_groups, student_data.department_id, session)
        
    return {"message": "Данные студента успешно обновлены!"}

@router.delete('/{id}', summary='Удалить студента по ID')
async def delete_student(
    id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = TransactionSessionDep,
) -> dict:
    student = await StudentDAO.find_one_or_none_by_id(data_id=id, session=session)
    if not student:
        raise HTTPException(status_code=404, detail=f"Студент с ID {id} не найден!")

    group = await GroupDAO.find_one_or_none_by_id(data_id=student.group_id, session=session)
    if not group:
        raise HTTPException(status_code=404, detail="Группа студента не найдена!")

    await StudentDAO.delete_one_by_id(data_id=id, session=session)
    background_tasks.add_task(balance_groups, group.department_id, session)
    return {"message": "Студент успешно удалён!"}

