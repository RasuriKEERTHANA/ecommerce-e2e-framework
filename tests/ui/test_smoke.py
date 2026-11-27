import re

import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_page_loads(page: Page):
    login = LoginPage(page).open()
    expect(page).to_have_title("Login - Test Shop")
    expect(login.submit_button).to_be_visible()


@pytest.mark.smoke
def test_valid_login_goes_to_products(page: Page):
    login = LoginPage(page).open()
    login.login("test@example.com", "Password123")
    expect(page).to_have_url(re.compile(r"/products$"))
    expect(login.nav_user).to_have_text("Hi, Test User")


def test_wrong_password_shows_error(page: Page):
    login = LoginPage(page).open()
    login.login("test@example.com", "WrongPass")
    login.expect_error("Invalid email or password")


def test_empty_fields_show_error(page: Page):
    login = LoginPage(page).open()
    login.login("", "")
    login.expect_error("Email and password are required")


def test_logout_returns_to_login(page: Page):
    login = LoginPage(page).open()
    login.login("test@example.com", "Password123")
    expect(login.nav_logout).to_be_visible()
    login.logout()
    expect(login.nav_login).to_be_visible()


def test_database_is_seeded(db):
    count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == 10