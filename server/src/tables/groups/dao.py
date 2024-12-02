from src.tables.dao.base import BaseDAO
from src.tables.groups.models import Group
from sqlalchemy import event
from random import randint


class GroupDAO(BaseDAO):
    model = Group

group_names = [str(name) for name in range(100, 991, 10)]
@event.listens_for(Group, 'before_insert')
def set_group_name(mapper, connection, target):
    if not target.name:
        random_index = randint(0, len(group_names) - 1)
        target.name = group_names.pop(random_index)

@event.listens_for(Group, 'before_delete')
def return_group_name(mapper, connection, target):
    group_names.append(target.name)