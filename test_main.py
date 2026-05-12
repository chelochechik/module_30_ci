from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

TEST_RECIPE = {
    "name": "блины",
    "cooking_time": 30,
    "ingredients": "some ingredients with valid length",
    "procedure": "some procedure with valid length",
}


def test_get_all_recipes():
    correct_json = [
        {"id": 3, "name": "борщ", "cooking_time": 180, "views": 10},
        {"id": 2, "name": "бутерброд", "cooking_time": 5, "views": 5},
        {"id": 1, "name": "string", "cooking_time": 10, "views": 5},
    ]
    response = client.get("/recipes")
    assert response.status_code == 200
    assert response.json() == correct_json


def test_creat_valid_recipe():
    response = client.post("/recipes", json=TEST_RECIPE)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "блины"
    assert data["cooking_time"] == 30
    assert data["views"] == 0


def test_get_valid_recipe(recipe_id: int = 4):
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    views = response.json()["views"]
    assert views == 1


def test_check_views_counter(recipe_id: int = 1):
    response_1 = client.get("/recipes")
    data = response_1.json()

    for item in data:
        if item["id"] == recipe_id:
            views_before = item.get("views")
            break

    response_2 = client.get(f"/recipes/{recipe_id}")
    views_after = response_2.json().get("views")
    assert views_after == views_before + 1


def test_get_invalid_recipe(recipe_id: int = 10):
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 404


def test_creat_recipe_with_invalid_cooking_time():
    invalid_json = {
        "name": "some name",
        "cooking_time": -60,
        "ingredients": "some ingredients with valid length",
        "procedure": "some procedure with valid length",
    }
    response = client.post("/recipes", json=invalid_json)
    assert response.status_code == 422


def test_creat_recipe_with_invalid_name():
    invalid_json = {
        "name": "ab",
        "cooking_time": 60,
        "ingredients": "some ingredients with valid length",
        "procedure": "some procedure with valid length",
    }
    response = client.post("/recipes", json=invalid_json)
    assert response.status_code == 422


def test_creat_recipe_with_empty_fields():
    invalid_json = {
        "name": "some name",
        "cooking_time": 60,
        "procedure": "some procedure with valid length",
    }
    response = client.post("/recipes", json=invalid_json)
    assert response.status_code == 422
