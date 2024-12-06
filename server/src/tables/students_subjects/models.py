from src.dao.database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey


class StudentSubject(Base):
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'), nullable=False)
    rate_id: Mapped[int] = mapped_column(ForeignKey('rates.id'), nullable=False)

    student: Mapped['Student'] = relationship('Student', back_populates='studentSubject')
    subject: Mapped['Subject'] = relationship('Subject', back_populates='studentSubject')
    rate: Mapped['Rate'] = relationship('Rate', back_populates='student_subject')
