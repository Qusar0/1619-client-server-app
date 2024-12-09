from pydantic import BaseModel, Field


class SStudentSubject(BaseModel):
    subject_id: int = Field(..., description="ID предмета")
    subject_name: str = Field(..., description="Название предмета")
    rate_id: int = Field(..., description="ID оценки")
    rate: str = Field(..., description="Оценка по предмету")


class SStudentSubjectUpdate(BaseModel):
    subject_id: int = Field(..., description="ID предмета")
    rate_id: int = Field(..., description="ID оценки")
