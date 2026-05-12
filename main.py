from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import engine, select, desc, asc

from database import engine, async_session
import models
import schemas

from schemas import RecipeOut


# STARTUP: создание таблиц
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(title="Кулинарная книга API",
              lifespan=lifespan)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/recipes",
         response_model=List[schemas.RecipeOut],
         status_code=200,
         summary="Список всех рецептов",
         description="Возвращает отсортированный список рецептов. Сортировка: сначала по убыванию просмотров, затем по возрастанию времени готовки"
         )
async def get_all_recipes(db: AsyncSession = Depends(get_db)) -> List[models.Recipe]:
    """
    **Сортировка:**
    1. По убыванию количества просмотров (views DESC)
    2. При равенстве просмотров - по возрастанию времени готовки (cooking_time ASC)

    **Поля ответа:**
    - id: уникальный идентификатор
    - name: название рецепта
    - views: количество просмотров
    - cooking_time: время готовки в минутах
    """
    result = await (db.execute(select(models.Recipe)
                        .order_by(desc(models.Recipe.views),asc(models.Recipe.cooking_time))))

    return result.scalars().all()


@app.get("/recipes/{recipe_id}",
         response_model=schemas.RecipeDetail,
         status_code=200,
         summary="Детальная информация о рецепте",
         description="Возвращает полную информацию о рецепте и увеличивает счетчик просмотров")
async def get_one_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)) -> models.Recipe:
    """
    **Автоматическое увеличение просмотров:**
    При каждом запросе поле views автоматически увеличивается на 1

    **Поля ответа:**
    - id: уникальный идентификатор
    - name: название рецепта
    - cooking_time: время готовки в минутах
    - ingredients: список ингредиентов (строка)
    - procedure: текстовое описание рецепта
    - views: текущее количество просмотров (после инкремента)

    **Коды ошибок:**
    - 404: Рецепт не найден
    """
    result = await (db.execute(select(models.Recipe)
                               .where(models.Recipe.id == recipe_id)))
    recipe = result.scalars().one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)
    return recipe


@app.post("/recipes",
          response_model=RecipeOut,
          status_code=201,
          summary="Создать новый рецепт",
          description="Создает новый рецепт в базе данных"
          )
async def add_recipe(recipe: schemas.RecipeIn, db: AsyncSession = Depends(get_db)) -> models.Recipe:
    """
    **Требуемые поля:**
    - name: название рецепта (обязательное)
    - cooking_time: время готовки в минутах (> 0)
    - ingredients: список ингредиентов через запятую или JSON
    - procedure: пошаговое описание

    **Валидация (автоматически код ошибки 422):**
    - name: str, 3 <= length <= 100
    - cooking_time: int > 0
    - ingredients: str, length >= 20
    - procedure: str, length >= 50
    """
    new_recipe = models.Recipe(**recipe.model_dump())

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)

    return new_recipe
