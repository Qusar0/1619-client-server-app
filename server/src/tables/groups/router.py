from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_maker import AsyncSessionDep
from src.tables.groups.schemas import SGroupsSelect
from src.tables.groups.dao import GroupDAO


router = APIRouter(prefix='/groups', tags=['Работа с группами'])

@router.get('/', summary='Получить все группы')
async def get_departments(session: AsyncSession = AsyncSessionDep) -> SGroupsSelect:
  groups = await GroupDAO.async_find_all(session)
  sgroups = SGroupsSelect(groups_name=[group.name for group in groups])
  return sgroups