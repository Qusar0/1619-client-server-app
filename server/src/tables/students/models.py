from src.dao.database import Base, photo_blob
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date


class Student(Base):
    first_name: Mapped[str]
    last_name: Mapped[str]
    birth_date: Mapped[date]
    enroll_date: Mapped[date] = mapped_column(server_default=func.current_date())
    photo: Mapped[photo_blob]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id'), nullable=True)

    group: Mapped['Group'] = relationship('Group', back_populates='students', lazy="selectin")
    studentSubject: Mapped[list['StudentSubject']] = relationship(
        'StudentSubject',
        back_populates='student',
        cascade='all, delete-orphan',
        lazy="selectin"
    )

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, group_id={self.group_id})")

    def __repr__(self):
        return str(self)