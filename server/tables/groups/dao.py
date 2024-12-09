from src.dao.base import BaseDAO
from src.tables.groups.models import Group
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from random import randint


class GroupDAO(BaseDAO[Group]):
    model = Group

    @classmethod
    async def add_group(cls, department_id: int, session: AsyncSession):
        new_group = cls.model()
        new_group.department_id = department_id
        session.add(new_group)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_group.id

group_names = [str(name) for name in range(100, 991, 10)]
@event.listens_for(Group, 'before_insert')
def set_group_name(mapper, connection, target):
    if not target.name:
        random_index = randint(0, len(group_names) - 1)
        target.name = group_names.pop(random_index)

@event.listens_for(Group, 'before_delete')
def return_group_name(mapper, connection, target):
    group_names.append(target.name)