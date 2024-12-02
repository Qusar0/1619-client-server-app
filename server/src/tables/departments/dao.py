from src.tables.dao.base import BaseDAO
from src.tables.departments.models import Department


class DepartmentDAO(BaseDAO):
    model = Department