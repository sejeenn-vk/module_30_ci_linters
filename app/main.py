from typing import List

import database
import models
import uvicorn
from fastapi import FastAPI
from schemas import RecipeDetail, RecipeIn, RecipeOut

app = FastAPI()


@app.get("/")
def main_page():
    return {"response": "Main page"}


@app.get("/recipes", response_model=List[RecipeOut])
async def get_all_recipes():
    result = await database.select_all_recipes()
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=List[RecipeDetail])
async def get_recipe_details(recipe_id):
    return await database.get_detail_recipe(recipe_id)


@app.post("/recipes", response_model=RecipeIn)
async def add_recipe(recipe: RecipeIn):
    new_recipe = models.Recipe(
        recipe_name=recipe.recipe_name,
        cooking_time=recipe.cooking_time,
        recipe_description=recipe.recipe_description,
    )
    ingredients = recipe.ingredients
    new_recipe_id = await database.add_new_recipe(new_recipe)
    ingredients_in_recipe = [
        models.IngredientsInRecipe(
            recipe_id=new_recipe_id,
            ingredient_id=i.ingredient_id,
            quantity=i.quantity,
        )
        for i in ingredients
    ]
    if new_recipe_id:
        await database.add_new_data(ingredients_in_recipe)
        return recipe


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
