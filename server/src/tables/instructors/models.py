from src.dao.database import Base, photo_blob
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date
from src.tables.departments.models import Department


class Instructor(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_date: Mapped[date]
    employ_date: Mapped[date] = mapped_column(server_default=func.current_date())
    photo: Mapped[photo_blob]
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    department: Mapped['Department'] = relationship('Department', back_populates='instructors', lazy="selectin")
    groups: Mapped[list['Group']] = relationship('Group', back_populates='instructor', lazy="selectin")

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, first_name={self.first_name}, last_name={self.last_name})")

    def __repr__(self):
        return str(self)