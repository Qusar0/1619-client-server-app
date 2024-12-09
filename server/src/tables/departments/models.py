from src.dao.database import Base, str_uniq
from sqlalchemy.orm import relationship, Mapped
from src.tables.subjects.models import Subject
from src.tables.students.models import Student
from src.tables.groups.models import Group
from src.tables.students_subjects.models import StudentSubject


class Department(Base):
    name: Mapped[str_uniq]

    instructors: Mapped[list['Instructor']] = relationship('Instructor', back_populates='department')
    groups: Mapped[list['Group']] = relationship('Group', back_populates='department')
    subjects: Mapped[list['Subject']] = relationship('Subject', back_populates='department')

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, name={self.name})")

    def __repr__(self):
        return str(self)