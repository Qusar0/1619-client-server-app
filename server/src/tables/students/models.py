from src.database import Base, int_pk, photo_blob
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date


class Student(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_date: Mapped[date]
    enroll_date: Mapped[date] = mapped_column(server_default=func.current_date())
    photo: Mapped[photo_blob]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=False)

    group: Mapped['Group'] = relationship('Group', back_populates='students')
    studentSubject: Mapped['StudentSubject'] = relationship('StudentSubject', back_populates='student')

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, first_name={self.first_name}, last_name={self.last_name})")

    def __repr__(self):
        return str(self)