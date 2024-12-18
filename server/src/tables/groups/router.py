from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.session_maker import SessionDep
from src.tables.groups.schemas import SGroupsSelect
from src.tables.groups.dao import GroupDAO


router = APIRouter(prefix='/groups', tags=['Работа с группами'])

@router.get('/', summary='Получить все группы')
async def get_departments(session: AsyncSession = SessionDep) -> SGroupsSelect:
  groups = await GroupDAO.find_all(session)
  sgroups = SGroupsSelect(groups_name=[group.name for group in groups])
  return sgroups