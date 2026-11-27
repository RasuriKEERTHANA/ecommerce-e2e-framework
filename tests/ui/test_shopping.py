import re

import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage

MOUSE = 1
BACKPACK = 9
OUT_OF_STOCK = 10


def test_search_returns_matching_product(page: Page):
    products = ProductsPage(page).open()
    products.search("shoes")
    expect(products.cards).to_have_count(1)
    expect(products.cards.first).to_contain_text("Running Shoes")


def test_search_with_no_match_shows_message(page: Page):
    products = ProductsPage(page).open()
    products.search("xyz")
    expect(products.no_results).to_have_text("No products found")


def test_category_filter(page: Page):
    products = ProductsPage(page).open()
    products.filter_by_category("Footwear")
    expect(products.cards).to_have_count(2)


def test_add_to_cart_requires_login(page: Page):
    products = ProductsPage(page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_have_text("Please log in to add items to your cart")


@pytest.mark.smoke
def test_add_to_cart_logged_in(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_have_text("Added Wireless Mouse to cart")


def test_out_of_stock_item_cannot_be_added(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(OUT_OF_STOCK)
    expect(products.message).to_have_text("Not enough stock")


def test_cart_shows_correct_total(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    products.add_to_cart(BACKPACK)
    expect(products.message).to_have_text("Added Backpack to cart")
    cart = CartPage(logged_in_page).open()
    expect(cart.items).to_have_count(2)
    expect(cart.total).to_have_text("64.98")


def test_remove_item_from_cart(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    cart = CartPage(logged_in_page).open()
    cart.remove(MOUSE)
    expect(cart.empty_message).to_have_text("Your cart is empty")


def test_increase_and_decrease_quantity(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    cart = CartPage(logged_in_page).open()
    cart.increase(MOUSE)
    expect(cart.quantity_of(MOUSE)).to_have_text("2")
    cart.decrease(MOUSE)
    expect(cart.quantity_of(MOUSE)).to_have_text("1")


def test_checkout_with_empty_fields_shows_error(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    checkout = CheckoutPage(logged_in_page).open()
    checkout.place_order()
    expect(checkout.error).to_have_text("All fields are required")


def test_checkout_with_invalid_card_shows_error(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    checkout = CheckoutPage(logged_in_page).open()
    checkout.fill_details("Test User", "12 Main St", "1234")
    checkout.place_order()
    expect(checkout.error).to_have_text("Invalid card number")


@pytest.mark.smoke
def test_successful_checkout(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")
    checkout = CheckoutPage(logged_in_page).open()
    checkout.fill_details("Test User", "12 Main St", "4111111111111111")
    checkout.place_order()
    expect(checkout.success).to_contain_text("placed successfully")
    expect(checkout.success).to_contain_text(re.compile(r"Order #\d+"))