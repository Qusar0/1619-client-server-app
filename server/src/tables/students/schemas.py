from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional


class SStudentSelect(BaseModel):
    id: int = Field(..., ge=1, description="ID студента")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    group: str = Field(..., description="Номер группы")
    department: str = Field(..., description="Название кафедры")


class SStudentAdd(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    birth_date: date = Field(..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    photo: Optional[bytes] = Field(None, description="Фото студента")

    @field_validator("birth_date")
    def validate_date_of_birth(cls, value):
        if value and value > datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value