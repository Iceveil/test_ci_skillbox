from typing import List, Dict, Any

from fastapi import FastAPI
import schemas
from database import session, engine, Base
from models import ReceptDetails, Recept
from sqlalchemy import select, update


app = FastAPI()


@app.get('/recipes')
async def get_recipes()-> List[Dict[str, Any]]:
    """Эндпоинт по получению всех рецпетов. Сортируется
    по количеству просмотров и времени приготовления"""
    query = select(Recept).order_by(Recept.count.desc(), Recept.time_to_done.asc())
    result = await session.execute(query)
    return result.scalars().all()


@app.get('/recipes/{recipes_id}')
async def get_recipes_by_id(recipes_id: int)-> Dict[str, Any]:
    """Эндпойнт по получению одного рецепта по его айди"""
    query = (select(ReceptDetails.recept_name, ReceptDetails.time_to_done,
                   ReceptDetails.description, ReceptDetails.ing_list)
            .where(ReceptDetails.parent_id == recipes_id))
    result = await session.execute(query)
    recept = result.all()

    upd_count = (update(Recept).where(Recept.id == recipes_id)
                 .values(count=Recept.count+1))

    await session.execute(upd_count)

    return {
        'Название': recept[0][0],
        'Время приготовления': recept[0][1],
        'Описание': recept[0][2],
        'Ингредиенты': recept[0][3]
    }



@app.post('/recipes')
async def add_recipes(recept: schemas.AddOneRecept)-> Dict[str, str]:
    """Добавление рецепта"""
    add_in_recepts = Recept(
        recept_name=recept.recept_name,
        count=0,
        time_to_done=recept.time_to_done,
    )

    session.add(add_in_recepts)
    await session.flush()

    new_recept = ReceptDetails(
        recept_name=recept.recept_name,
        time_to_done=recept.time_to_done,
        ing_list=recept.ing_list,
        description=recept.description,
        parent_id=add_in_recepts.id
    )

    session.add(new_recept)
    await session.commit()
    return {'OK': f'Рецепт {recept.recept_name} добавлен'}


@app.post('/create_db')
async def create_db()-> Dict[str, bool]:
    """Создание таблиц. Запустить перед остальными операциями"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return {'ok': True}