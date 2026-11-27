from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.total = page.get_by_test_id("checkout-total")
        self.name_input = page.get_by_test_id("checkout-name")
        self.address_input = page.get_by_test_id("checkout-address")
        self.card_input = page.get_by_test_id("checkout-card")
        self.place_order_button = page.get_by_test_id("place-order")
        self.error = page.get_by_test_id("checkout-error")
        self.success = page.get_by_test_id("order-success")

    def open(self):
        self.page.goto("/checkout")
        return self

    def fill_details(self, name: str, address: str, card: str):
        self.name_input.fill(name)
        self.address_input.fill(address)
        self.card_input.fill(card)

    def place_order(self):
        self.place_order_button.click()