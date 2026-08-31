import pytest
from sqlalchemy import select
from ..models import Recept, ReceptDetails


@pytest.mark.asyncio
async def test_get_recipes(client, db_session):
    print('ТЕСТ 1 ЗАПУСТИЛСЯ')
    rec = Recept(
        recept_name = 'chicken',
        time_to_done = 25,
        count=0
    )

    db_session.add(rec)
    await db_session.commit()

    from sqlalchemy import select
    result = await db_session.execute(select(Recept))
    recipes = result.scalars().all()
    print(f"Рецепты в БД: {[r.recept_name for r in recipes]}")

    resp = await client.get('/recipes')

    assert resp.status_code == 200
    data = resp.read()
    print(data)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_recept_by_id(client, db_session):
    print('ТЕСТ 2 ЗАПУСТИЛСЯ!')
    rec = ReceptDetails(
        recept_name='chicken',
        time_to_done = 25,
        ing_list = 'chicken solt oil',
        description = 'very nice',
        parent_id = 1,
    )

    db_session.add(rec)
    await db_session.commit()

    from sqlalchemy import select
    result = await db_session.execute(select(ReceptDetails))
    recipes = result.scalars().all()
    print(f"Рецепты в БД: {[r.recept_name for r in recipes]}")

    resp = await client.get('/recipes/1')
    assert resp.status_code == 200
    data = resp.json()
    print(data)
    assert data.get('Название') == 'chicken'


@pytest.mark.asyncio
async def test_post_recipes(client, db_session):
    rec = {
        'recept_name' : 'chicken1',
        'time_to_done': 25,
        'ing_list' : 'chicken solt oil',
        'description' : 'very nice',
    }

    resp = await client.post('/recipes', json=rec)
    assert resp.status_code == 200
    data = resp.json()
    print(data)
    assert data.get('OK') == 'Рецепт chicken1 добавлен'

    result = await db_session.execute(select(Recept).where(Recept.recept_name=='chicken1'))
    res = result.scalar_one_or_none()
    assert res.recept_name == 'chicken1'
    assert res.time_to_done == 25

    result_2 = await db_session.execute(select(ReceptDetails).where(ReceptDetails.id == 1))
    res_2 = result_2.scalar_one_or_none()
    assert res_2.recept_name == 'chicken'
    assert res_2.time_to_done == 25
