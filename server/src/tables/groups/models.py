from src.database import Base, str_uniq, int_pk
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey


class Group(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    instructor_id: Mapped[int] = mapped_column(ForeignKey('instructors.id'), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    instructor: Mapped['Instructor'] = relationship('Instructor', back_populates='groups')
    department: Mapped['Department'] = relationship('Department', back_populates='groups')
    students: Mapped[list['Student']] = relationship('Student', back_populates='group')

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, name={self.name})")

    def __repr__(self):
        return str(self)