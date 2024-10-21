from models import Ingredient, IngredientsInRecipe, Recipe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./app.db")
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def select_all_recipes():
    """
    Функция получения всех рецептов из базы данных с сортировкой
    по количеству просмотров, а если просмотры одинаковы, то по времени
    приготовления рецепта.
    - Название рецепта.
    - Время приготовления.
    - Количество просмотров.
    :return: Список рецептов.
    """
    async with async_session() as session:
        stmt = select(Recipe).order_by(-Recipe.views, Recipe.cooking_time)
        return await session.execute(stmt)


async def get_detail_recipe(recipe_id: int):
    """
    Функция получения детальной информации о рецепте. Которая включает в себя:
    - id
    - Название рецепта.
    - Время приготовления.
    - Список ингредиентов.
    - Текстовое описание.
    :param recipe_id: Id рецепта, который хотим посмотреть.
    :return:
    """ # noqa
    async with async_session() as session:
        result = await session.execute(
            select(Recipe).filter(Recipe.id == recipe_id)
        )
        result_2 = await session.execute(
            select(
                IngredientsInRecipe.quantity,
                Ingredient.ingredient_name,
                Ingredient.ingredient_description,
            )
            .join(
                Ingredient, Ingredient.id == IngredientsInRecipe.ingredient_id
            )
            .where(IngredientsInRecipe.recipe_id == recipe_id)
        )

        recipe = result.scalars().one()
        ingredients = result_2.fetchall()

        recipe.views += 1
        await session.commit()

        return [
            {
                "id": recipe.id,
                "recipe_name": recipe.recipe_name,
                "cooking_time": recipe.cooking_time,
                "description": recipe.recipe_description,
                "ingredients": [
                    {
                        "name": i.ingredient_name,
                        "description": i.ingredient_description,
                        "quantity": i.quantity,
                    }
                    for i in ingredients
                ],
            },
        ]


async def add_new_data(*objs):
    """
    Функция наполнения базы данных. Вставляются объекты рецептов,
    ингредиентов или связей рецептов с ингредиентами.
    :param objs: Список объектов (Recipe, Ingredients, IngredientsInRecipe)
    :return: None
    """
    async with async_session() as session:
        async with session.begin():
            session.add_all(*objs)


async def add_new_recipe(new_recipe):
    """
    Функция создания нового рецепта. Принимает объект рецепта и возвращает
    полученный при его создании id
    :param new_recipe:
    :return: recipe_id
    """
    async with async_session() as session:
        async with session.begin():
            session.add(new_recipe)
            await session.commit()
            return new_recipe.id
