from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, datetime
from typing import Optional


class SInstructorSelect(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя куратора, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия куратора, от 1 до 50 символов")
    department_id: int = Field(..., ge=1, description="ID кафедры")
    department: str = Field(..., description="Название кафедры")
    groups: Optional[list[str]] = Field(None, description="Группы куратора")


class SInstructorAdd(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя куратора, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия куратора, от 1 до 50 символов")
    birth_date: date = Field(..., description="Дата рождения куратора в формате ГГГГ-ММ-ДД")
    photo: Optional[bytes] = Field(None, description="Фото куратора")
    department_id: int = Field(..., ge=1, description="ID кафедры куратора")
    
    @field_validator("birth_date")
    def validate_date_of_birth(cls, value):
        if value and value > datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value