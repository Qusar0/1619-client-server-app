from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_maker import AsyncSessionDep
from src.tables.departments.schemas import SDepartmentsSelect
from src.tables.departments.dao import DepartmentDAO


router = APIRouter(prefix='/departments', tags=['Работа с кафедрами'])

@router.get('/', summary='Получить все кафедры')
async def get_departments(session: AsyncSession = AsyncSessionDep) -> SDepartmentsSelect:
  departments = await DepartmentDAO.async_find_all(session)
  sdepartments = SDepartmentsSelect(departments_name=[department.name for department in departments ])
  return sdepartments