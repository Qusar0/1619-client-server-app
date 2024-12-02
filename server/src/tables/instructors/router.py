from fastapi import APIRouter, Depends
from src.tables.instructors.dao import InstructorDAO
from src.tables.instructors.schemas import SInstructorSelect, SInstructorAdd
from typing import Union


router = APIRouter(prefix='/instructors', tags=['Работа с кураторами'])

@router.get('/', summary='Получить всех кураторов')
async def get_instructors() -> list[SInstructorSelect]:
    return await InstructorDAO.find_full_data_instructors()

@router.get('/{id}', summary='Получить куратора по ID')
async def get_instructor_by_id(instructor_id: int) -> Union[SInstructorSelect, dict]:
    result = await InstructorDAO.find_full_data_instructor_by_id(instructor_id)
    if result is None:
        return {'message': f'Куратор с ID {instructor_id} не найден!'}
    
    return result

@router.post('/add/', summary='Добавить нового куратора')
async def add_instructor(instructor: SInstructorAdd) -> dict:
    check = await InstructorDAO.add_instructor(instructor.model_dump())
    if check:
        return {"message": "Куратор успешно добавлен!", "instructor": instructor}
    else:
        return {"message": "Ошибка при добавлении куратора!"}
    
@router.delete('/del/{id}', summary='Удалить куратора по ID')
async def delete_instructor(instuctor_id: int) -> dict:
    check = await InstructorDAO.delete_instructor_by_id(instuctor_id)
    if check:
        return {"message": f"Куратор с ID {instuctor_id} удален!"}
    else:
        return {"message": "Ошибка при удалении куратора!"}
    
