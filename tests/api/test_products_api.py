import pytest
from jsonschema import validate

from utils.schemas import PRODUCT_SCHEMA

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_list_products_returns_all_with_valid_schema(api):
    response = api.get("/api/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 10
    for product in products:
        validate(product, PRODUCT_SCHEMA)


def test_search_by_name(api):
    products = api.get("/api/products", params={"search": "shoes"}).json()
    assert [p["name"] for p in products] == ["Running Shoes"]


def test_search_with_no_match_returns_empty_list(api):
    response = api.get("/api/products", params={"search": "xyz"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_by_category(api):
    products = api.get("/api/products", params={"category": "Footwear"}).json()
    assert len(products) == 2
    assert {p["category"] for p in products} == {"Footwear"}


def test_search_and_category_combined(api):
    products = api.get(
        "/api/products", params={"search": "mouse", "category": "Electronics"}
    ).json()
    assert len(products) == 1
    assert products[0]["name"] == "Wireless Mouse"


def test_get_single_product(api):
    response = api.get("/api/products/1")
    assert response.status_code == 200
    validate(response.json(), PRODUCT_SCHEMA)
    assert response.json()["name"] == "Wireless Mouse"


def test_get_unknown_product_returns_404(api):
    response = api.get("/api/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_get_product_with_non_numeric_id_returns_422(api):
    response = api.get("/api/products/abc")
    assert response.status_code == 422