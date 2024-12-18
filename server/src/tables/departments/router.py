from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_maker import SessionDep
from src.tables.departments.schemas import SDepartmentSelect
from src.tables.departments.dao import DepartmentDAO


router = APIRouter(prefix='/departments', tags=['Работа с кафедрами'])

@router.get('/', summary='Получить все кафедры')
async def get_departments(session: AsyncSession = SessionDep) -> list[SDepartmentSelect]:  
  departments = await DepartmentDAO.find_all(session)
  sdepartments = [SDepartmentSelect(department_id=department.id,
                                  department_name=department.name) for department in departments]
  return sdepartments