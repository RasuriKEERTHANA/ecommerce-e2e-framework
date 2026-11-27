import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

MOUSE = 1
DENIM_JACKET = 7  # stock = 10 in the seed data

# Tag every test in this file as part of the full regression run
pytestmark = pytest.mark.regression


def test_cart_page_requires_login(page: Page):
    cart = CartPage(page).open()
    expect(cart.message).to_have_text("Please log in to view your cart")


def test_checkout_requires_login(page: Page):
    checkout = CheckoutPage(page).open()
    checkout.fill_details("Test User", "12 Main St", "4111111111111111")
    checkout.place_order()
    expect(checkout.error).to_have_text("Please log in to check out")


def test_cannot_increase_quantity_beyond_stock(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(DENIM_JACKET)
    expect(products.message).to_contain_text("Added")

    cart = CartPage(logged_in_page).open()
    # Quantity is 1; click + until it reaches the stock limit of 10
    for expected_qty in range(2, 11):
        cart.increase(DENIM_JACKET)
        expect(cart.quantity_of(DENIM_JACKET)).to_have_text(str(expected_qty))

    # One more click goes over the limit
    cart.increase(DENIM_JACKET)
    expect(cart.message).to_have_text("Not enough stock")
    expect(cart.quantity_of(DENIM_JACKET)).to_have_text("10")


def test_checkout_with_empty_cart_shows_error(logged_in_page: Page):
    checkout = CheckoutPage(logged_in_page).open()
    checkout.fill_details("Test User", "12 Main St", "4111111111111111")
    checkout.place_order()
    expect(checkout.error).to_have_text("Cart is empty")


def test_search_is_case_insensitive(page: Page):
    products = ProductsPage(page).open()
    products.search("SHOES")
    expect(products.cards).to_have_count(1)
    expect(products.cards.first).to_contain_text("Running Shoes")


def test_cart_total_updates_when_quantity_increases(logged_in_page: Page):
    products = ProductsPage(logged_in_page).open()
    products.add_to_cart(MOUSE)
    expect(products.message).to_contain_text("Added")

    cart = CartPage(logged_in_page).open()
    expect(cart.total).to_have_text("19.99")
    cart.increase(MOUSE)
    expect(cart.total).to_have_text("39.98")


@pytest.mark.parametrize(
    "email, password",
    [
        ("nobody@example.com", "Password123"),   # unknown email
        ("test@example.com", "password123"),     # password is case-sensitive
        ("test@example.com", " "),               # whitespace-only password
    ],
    ids=["unknown-email", "wrong-case-password", "blank-password"],
)
def test_invalid_login_combinations(page: Page, email, password):
    login = LoginPage(page).open()
    login.login(email, password)
    login.expect_error("Invalid email or password")