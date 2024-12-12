from pydantic import create_model, BaseModel, Field


DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))

class SDepartmentsSelect(BaseModel):
  departments_name: list[str] = Field(..., description="Название кафедр")