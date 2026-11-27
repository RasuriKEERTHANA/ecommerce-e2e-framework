from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.message = page.get_by_test_id("cart-message")
        self.items = page.get_by_test_id("cart-item")
        self.empty_message = page.get_by_test_id("empty-cart")
        self.total = page.get_by_test_id("cart-total-value")
        self.checkout_button = page.get_by_test_id("checkout-button")

    def open(self):
        self.page.goto("/cart")
        return self

    def increase(self, product_id: int):
        self.page.get_by_test_id(f"increase-{product_id}").click()

    def decrease(self, product_id: int):
        self.page.get_by_test_id(f"decrease-{product_id}").click()

    def remove(self, product_id: int):
        self.page.get_by_test_id(f"remove-{product_id}").click()

    def quantity_of(self, product_id: int):
        return self.page.get_by_test_id("cart-item").filter(
            has=self.page.get_by_test_id(f"remove-{product_id}")
        ).get_by_test_id("cart-item-qty")