from fastapi import APIRouter
from src.tables.students.dao import StudentDAO
from src.tables.instructors.dao import InstructorDAO
from src.tables.students.schemas import SStudentAdd, SStudentSelect, SStudentUpdate
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from src.dao.session_maker import SessionDep, TransactionSessionDep

from src.tables.groups.dao import GroupDAO
from src.dao.balanced_function import balanced_function
from src.tables.departments.schemas import DepartmentModel

router = APIRouter(prefix='/students', tags=['Работа со студентами'])

@router.get('/', summary='Получить всех студентов')
async def get_students(session: AsyncSession = SessionDep) -> list[SStudentSelect]:
    return await StudentDAO.find_full_data_students(session)

@router.post('/add/', summary='Добавить студента')
async def add_student(department_id: int, student: SStudentAdd, session: AsyncSession = TransactionSessionDep):
    department = DepartmentModel(department_id=department_id)

    instructors = await InstructorDAO.find_all(session=session, filters=department)
    if not instructors:
            return {"message": "Невозможно добавить студента на кафедру без куратора!"}

    current_groups = await GroupDAO.find_all(session=session, filters=department)
    if len(current_groups) == 0:
        group_id = await GroupDAO.add_group(department_id=department_id, session=session)
    else:
        group_id = current_groups[0].id

    check = await StudentDAO.add_student(group_id=group_id, student=student, session=session)
    if check:
        await balanced_function(department_id=department_id, session=session)
        return {"message": "Студент успешно добавлен!"}
    return {"message": "Студент не был добавлен!"}

@router.put('/update/{id}', summary='Обновить данные студента по ID')
async def update_student(id: int, student_data: SStudentUpdate, session: AsyncSession = TransactionSessionDep):# -> dict
    student = await StudentDAO.find_full_data_student_by_id(student_id=id, session=session)
    if student is None:
        return
    
    student_department_id = student.get('department_id')

    if student_department_id != student_data.department_id:
        department = DepartmentModel(department_id=student_data.department_id)
        instructors = await InstructorDAO.find_all(session=session, filters=department)
        if len(instructors) < 1:
            return {"message": "Невозможно перевести студента на кафедру без кураторов!"}

    check = await StudentDAO.update_student(student_id=student.get('id'), updated_data=student_data, session=session)
    if check:
        await balanced_function(department_id=student_data.department_id, session=session)
        if student_department_id != student_data.department_id:
            await balanced_function(department_id=student_department_id, session=session)
        return {"message": "Данные студента успешно обновлены!"}
    else:
        return {"message": "Ошибка при обновлении данных студента!"}


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
