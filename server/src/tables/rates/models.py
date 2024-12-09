from src.dao.database import Base, str_uniq
from sqlalchemy.orm import relationship, Mapped


class Rate(Base):
    name: Mapped[str_uniq]

    student_subject: Mapped[list['StudentSubject']] = relationship('StudentSubject', back_populates='rate')
