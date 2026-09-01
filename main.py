from typing import Any, Dict, List

from fastapi import Depends, FastAPI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import Base, engine, get_db
from models import Recept, ReceptDetails

app = FastAPI()


@app.get("/recipes")
async def get_recipes(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Эндпоинт по получению всех рецпетов. Сортируется
    по количеству просмотров и времени приготовления"""
    query = select(Recept).order_by(Recept.count.desc(), Recept.time_to_done.asc())
    result = await db.execute(query)
    recipes = result.scalars().all()
    return [r.to_dict() for r in recipes]


@app.get("/recipes/{recipes_id}")
async def get_recipes_by_id(
    recipes_id: int, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Эндпойнт по получению одного рецепта по его айди"""
    query = select(
        ReceptDetails.recept_name,
        ReceptDetails.time_to_done,
        ReceptDetails.description,
        ReceptDetails.ing_list,
    ).where(ReceptDetails.parent_id == recipes_id)
    result = await db.execute(query)
    recept = result.all()

    upd_count = (
        update(Recept).where(Recept.id == recipes_id).values(count=Recept.count + 1)
    )

    await db.execute(upd_count)

    return {
        "Название": recept[0][0],
        "Время приготовления": recept[0][1],
        "Описание": recept[0][2],
        "Ингредиенты": recept[0][3],
    }


@app.post("/recipes")
async def add_recipes(
    recept: schemas.AddOneRecept, db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Добавление рецепта"""
    add_in_recepts = Recept(
        recept_name=recept.recept_name,
        count=0,
        time_to_done=recept.time_to_done,
    )

    db.add(add_in_recepts)
    await db.flush()

    new_recept = ReceptDetails(
        recept_name=recept.recept_name,
        time_to_done=recept.time_to_done,
        ing_list=recept.ing_list,
        description=recept.description,
        parent_id=add_in_recepts.id,
    )

    db.add(new_recept)
    await db.commit()
    return {"OK": f"Рецепт {recept.recept_name} добавлен"}


@app.post("/create_db")
async def create_db() -> Dict[str, bool]:
    """Создание таблиц. Запустить перед остальными операциями"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return {"ok": True}
