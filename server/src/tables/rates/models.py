from src.database import Base, int_pk, str_uniq
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import date


class Rate(Base):
    id: Mapped[int_pk]
    name: Mapped[str_uniq]

    student_subject: Mapped[list['StudentSubject']] = relationship('StudentSubject', back_populates='rate')
