from pydantic import BaseModel, Field


class AllRecepts(BaseModel):
    """Схема всех рецептов"""
    recept_name: str
    count: int = Field(ge=0)
    time_to_done: int = Field(ge=0)


class AddOneRecept(BaseModel):
    """Схема одного рецепта"""
    recept_name: str
    time_to_done: int = Field(ge=0)
    ing_list: str
    description: str


class OneRecept(AddOneRecept):
    id: int
