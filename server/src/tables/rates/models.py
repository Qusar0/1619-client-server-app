from src.dao.database import Base, str_uniq
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date


class Rate(Base):
    name: Mapped[str_uniq]

    student_subject: Mapped[list['StudentSubject']] = relationship('StudentSubject', back_populates='rate')
