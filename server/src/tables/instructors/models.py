from src.database import Base, int_pk, photo_blob
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date
from src.tables.departments.models import Department


class Instructor(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_date: Mapped[date]
    employ_date: Mapped[date] = mapped_column(server_default=func.current_date())
    photo: Mapped[photo_blob]
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    department: Mapped['Department'] = relationship('Department', back_populates='instructors')
    groups: Mapped[list['Group']] = relationship('Group', back_populates='instructor')

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, first_name={self.first_name}, last_name={self.last_name})")

    def __repr__(self):
        return str(self)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date,
            'photo': self.photo,
            'department_id': self.department_id
        }