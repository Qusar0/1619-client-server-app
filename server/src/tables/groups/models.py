from src.dao.database import Base, str_uniq
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey


class Group(Base):
    name: Mapped[str_uniq]
    instructor_id: Mapped[int] = mapped_column(ForeignKey('instructors.id'), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    instructor: Mapped['Instructor'] = relationship('Instructor', back_populates='groups', lazy="selectin")
    department: Mapped['Department'] = relationship('Department', back_populates='groups', lazy="selectin")
    students: Mapped[list['Student']] = relationship('Student', back_populates='group', lazy="selectin")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, instructor_id={self.instructor_id})"

    def __repr__(self):
        return str(self)