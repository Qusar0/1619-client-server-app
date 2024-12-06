from fastapi import APIRouter
from src.tables.instructors.dao import InstructorDAO
from src.tables.instructors.schemas import SInstructorSelect, SInstructorAdd
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.session_maker import SessionDep, TransactionSessionDep
from src.dao.balanced_function import balanced_function

router = APIRouter(prefix='/instructors', tags=['Работа с кураторами'])

@router.get('/', summary='Получить всех кураторов')
async def get_instructors(session: AsyncSession = SessionDep) -> list[SInstructorSelect]:
    return await InstructorDAO.find_full_data_instructors(session)

@router.get('/{id}', summary='Получить куратора по ID')
async def get_instructor_by_id(instructor_id: int, session: AsyncSession = SessionDep) -> Union[SInstructorSelect, dict]:
    result = await InstructorDAO.find_full_data_instructor_by_id(session=session, instructor_id=instructor_id)
    if result is None:
        return {'message': f'Куратор с ID {instructor_id} не найден!'}
    
    return result

@router.post('/add/', summary='Добавить нового куратора')
async def add_instructor(instructor: SInstructorAdd, session: AsyncSession = TransactionSessionDep) -> dict:
    check = await InstructorDAO.add(session=session, values=instructor)
    if check:
        await balanced_function(department_id=instructor.department_id, session=session)
        return {"message": "Куратор успешно добавлен!", "instructor": instructor}
    else:
        return {"message": "Ошибка при добавлении куратора!"}
    
@router.put('/update/{id}', summary='Обновить данные куратора по ID')
async def update_instructor(id: int, instructor_data: SInstructorAdd, session: AsyncSession = TransactionSessionDep) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if instructor is None:
        return
    
    instructor_department_id = instructor.department_id

    check = await InstructorDAO.update_one_by_id(session=session, data_id=id, values=instructor_data)
    if check:
        await balanced_function(department_id=instructor_data.department_id, session=session)
        if instructor_department_id != instructor_data.department_id:
            await balanced_function(department_id=instructor_department_id, session=session)
        return {"message": "Данные куратора успешно обновлены!"}
    else:
        return {"message": "Ошибка при обновлении данных куратора!"}

@router.delete('/delete/{id}', summary='Удалить куратора по ID')
async def delete_instructor(id: int, session: AsyncSession = TransactionSessionDep):
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if instructor:
        await InstructorDAO.delete_one_by_id(data_id=id, session=session)
        await balanced_function(department_id=instructor.department_id, session=session)
        return {"message": "Данные куратора успешно обновлены!"}
    return {"message": "Ошибка при обновлении данных куратора!"}
