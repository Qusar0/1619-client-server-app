from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from src.tables.instructors.dao import InstructorDAO
from src.tables.students.dao import StudentDAO
from src.tables.instructors.schemas import SInstructorSelect, SInstructorAdd, SInstructorUpdate
from src.tables.departments.schemas import DepartmentModel

from src.dao.session_maker import SessionDep, TransactionSessionDep
from src.dao.group_balancer import GroupBalancer


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
        balancer = GroupBalancer(department_id=instructor.department_id, session=session)
        await balancer.balance()
        return {"message": "Куратор успешно добавлен!", "instructor": instructor}
    else:
        return {"message": "Ошибка при добавлении куратора!"}
    
@router.put('/update/{id}', summary='Обновить данные куратора по ID')
async def update_instructor(id: int, instructor_data: SInstructorUpdate, session: AsyncSession = TransactionSessionDep) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if instructor is None:
        return {'message': f'Куратор с ID {id} не найден!'}
    
    instructor_department_id = instructor.department_id
    if instructor_data.department_id and instructor_department_id != instructor_data.department_id:
        department = DepartmentModel(department_id=instructor_department_id)
        instructors = await InstructorDAO.find_all(session=session, filters=department)
        if len(instructors) == 1:
            return {"message": "Невозможно перевести последнего куратора с кафедры на которой числятся студенты!"}

    check = await InstructorDAO.update_one_by_id(session=session, data_id=id, values=instructor_data)
    if check:
        if instructor_data.department_id:
            prev_department_balancer = GroupBalancer(department_id=instructor_data.department_id, session=session)
            await prev_department_balancer.balance()
        if instructor_department_id != instructor_data.department_id:
            curr_department_balancer = GroupBalancer(department_id=instructor_department_id, session=session)
            await curr_department_balancer.balance()
        return {"message": "Данные куратора успешно обновлены!"}
    else:
        return {"message": "Ошибка при обновлении данных куратора!"}

@router.delete('/delete/{id}', summary='Удалить куратора по ID')
async def delete_instructor(id: int, session: AsyncSession = TransactionSessionDep) -> dict:
    instructor = await InstructorDAO.find_one_or_none_by_id(data_id=id, session=session)
    if instructor:
        department = DepartmentModel(department_id=instructor.department_id)

        students = await StudentDAO.students_by_department_id(department_id=instructor.department_id, session=session)
        instructors = await InstructorDAO.find_all(session=session, filters=department)

        if len(instructors) <= 1 and students:
            return {"message": "Нельзя удалить последнего преподавателя, так как на кафедре числятся студенты!"}

        await InstructorDAO.delete_one_by_id(data_id=id, session=session)
        balancer = GroupBalancer(department_id=instructor.department_id, session=session)
        await balancer.balance()
        return {"message": "Данные куратора успешно удалены!"}

    return {"message": "Ошибка при удалении данных куратора!"}
