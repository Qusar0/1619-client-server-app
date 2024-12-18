from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
import json

from src.tables.instructors.dao import InstructorDAO
from src.tables.students.dao import StudentDAO
from src.tables.instructors.schemas import SInstructorSelect, SInstructorAdd, SInstructorUpdate
from src.tables.departments.schemas import DepartmentModel

from src.dao.session_maker import SessionDep, TransactionSessionDep
from src.dao.group_balancer import balance_groups
from src.connection_manager import manager


router = APIRouter(prefix='/instructors', tags=['Работа с кураторами'])

@router.get('/', summary='Получить всех кураторов')
async def get_instructors(session: AsyncSession = SessionDep) -> Optional[list[SInstructorSelect]]:
    return await InstructorDAO.find_full_data_instructors(session)

@router.get('/{id}', summary='Получить куратора по ID')
async def get_instructor_by_id(instructor_id: int, session: AsyncSession = SessionDep) -> Union[SInstructorSelect, dict]:
    result = await InstructorDAO.find_full_data_instructor_by_id(session=session, instructor_id=instructor_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f'Куратор с ID {instructor_id} не найден!')
    return result

@router.post('/add/', summary='Добавить нового куратора')
async def add_instructor(
    instructor: SInstructorAdd,
    background_tasks: BackgroundTasks,
    session: AsyncSession = SessionDep,
) -> dict:
    check = await InstructorDAO.add(session=session, values=instructor)
    if check:
        background_tasks.add_task(balance_groups, instructor.department_id, session)
        instructors = await get_instructors(session)
        print(instructors)
        await manager.broadcast(json.dumps({
            "category": "instructors",
            "data": [instructor.model_dump() for instructor in instructors]
        }))
        return {"message": "Куратор успешно добавлен!", "instructor": instructor}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при добавлении куратора!")
    
@router.put('/update/{id}', summary='Обновить данные куратора по ID')
async def update_instructor(
    id: int,
    instructor_data: SInstructorUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = TransactionSessionDep,
) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if instructor is None:
        return {'message': f'Куратор с ID {id} не найден!'}
    
    instructor_department_id = instructor.department_id
    if instructor_data.department_id and instructor_department_id != instructor_data.department_id:
        department = DepartmentModel(department_id=instructor_department_id)
        instructors = await InstructorDAO.find_all(session=session, filters=department)
        if len(instructors) == 1:
            raise HTTPException(status_code=400, detail="Невозможно перевести последнего куратора с кафедры на которой числятся студенты!")

    check = await InstructorDAO.update_one_by_id(session=session, data_id=id, values=instructor_data)
    if not check:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении данных куратора!")

    if instructor_data.department_id:
        background_tasks.add_task(balance_groups, instructor_data.department_id, session)
    if instructor_department_id != instructor_data.department_id:
        background_tasks.add_task(balance_groups, instructor_department_id, session)

    return {"message": "Данные куратора успешно обновлены!"}

@router.delete('/delete/{id}', summary='Удалить куратора по ID')
async def delete_instructor(
    id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = TransactionSessionDep,
) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if not instructor:
        raise HTTPException(status_code=404, detail=f'Куратор с ID {id} не найден!')

    department = DepartmentModel(department_id=instructor.department_id)

    students = await StudentDAO.students_by_department_id(department_id=instructor.department_id, session=session)
    instructors = await InstructorDAO.find_all(session=session, filters=department)

    if len(instructors) <= 1 and students:
        raise HTTPException(status_code=400, detail="Нельзя удалить последнего преподавателя, так как на кафедре числятся студенты!")

    await InstructorDAO.delete_one_by_id(data_id=id, session=session)
    background_tasks.add_task(balance_groups, instructor.department_id, TransactionSessionDep)
    return {"message": "Данные куратора успешно удалены!"}

