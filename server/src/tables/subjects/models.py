from src.database import Base, str_uniq, int_pk
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.tables.students_subjects.models import StudentSubject

class Subject(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'), nullable=False)

    department: Mapped['Department'] = relationship('Department', back_populates='subjects')
    studentSubject: Mapped['StudentSubject'] = relationship('StudentSubject', back_populates='subject')

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, name={self.name})")

    def __repr__(self):
        return str(self)