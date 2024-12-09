from pydantic import BaseModel, Field


class SStudentSubjectSelect(BaseModel):
    subject_id: int = Field(..., description="ID предмета")
    subject_name: str = Field(..., description="Название предмета")
    rate_id: int = Field(..., description="ID оценки")
    rate: str = Field(..., description="Оценка по предмету")


class SStudentSubjectAdd(BaseModel):
    student_id: int = Field(..., description="ID студента")
    subject_id: int = Field(..., description="ID предмета")
    rate_id: int = Field(1, description="ID отметки")


class SStudentSubjectUpdate(BaseModel):
    subject_id: int = Field(..., description="ID предмета")
    rate_id: int = Field(..., description="ID оценки")
