from pydantic import BaseModel, Field


class SGroupsSelect(BaseModel):
  groups_name: list[str] = Field(..., description="Название групп")