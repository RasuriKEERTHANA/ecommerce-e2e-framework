import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_login_page_loads(page: Page):
    page.goto("/login")
    expect(page).to_have_title("Login - Test Shop")
    expect(page.get_by_test_id("login-form")).to_be_visible()


@pytest.mark.smoke
def test_valid_login_goes_to_products(page: Page):
    page.goto("/login")
    page.get_by_test_id("login-email").fill("test@example.com")
    page.get_by_test_id("login-password").fill("Password123")
    page.get_by_test_id("login-submit").click()
    expect(page).to_have_url(re.compile(r"/products$"))
    expect(page.get_by_test_id("nav-user")).to_have_text("Hi, Test User")


def test_database_is_seeded(db):
    count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    assert count == 10