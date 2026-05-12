from pydantic import BaseModel, Field


class RecipeIn(BaseModel): # для POST
    name: str = Field(..., min_length=3, max_length=100)
    cooking_time: int = Field(..., gt=0)
    ingredients: str = Field(..., min_length=10)
    procedure: str = Field(..., min_length=30)


class RecipeOut(BaseModel): # Для GET всех рецептов
    id: int
    name: str
    cooking_time: int
    views: int

    class Config:
        from_attributes = True


class RecipeDetail(BaseModel): # Для GET одного рецепта
    id: int
    name: str
    cooking_time: int
    ingredients: str
    procedure: str
    views: int

    class Config:
        from_attributes = True
