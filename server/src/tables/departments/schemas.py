from pydantic import create_model, BaseModel, Field


DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))

class SDepartmentSelect(BaseModel):
  department_id: int = Field(..., description="ID кафедры")
  department_name: str = Field(..., description="Название кафедры")