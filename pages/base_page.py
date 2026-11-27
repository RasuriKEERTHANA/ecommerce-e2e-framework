from playwright.sync_api import Page


class BasePage:
    """Things every page shares: the nav bar and common actions."""

    def __init__(self, page: Page):
        self.page = page
        self.nav_user = page.get_by_test_id("nav-user")
        self.nav_cart = page.get_by_test_id("nav-cart")
        self.nav_products = page.get_by_test_id("nav-products")
        self.nav_login = page.get_by_test_id("nav-login")
        self.nav_logout = page.get_by_test_id("nav-logout")

    def logout(self):
        self.nav_logout.click()
        self.page.wait_for_url("**/login")