from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ProductsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_test_id("search-input")
        self.category_filter = page.get_by_test_id("category-filter")
        self.search_button = page.get_by_test_id("search-button")
        self.message = page.get_by_test_id("products-message")
        self.result_count = page.get_by_test_id("result-count")
        self.cards = page.get_by_test_id("product-card")
        self.no_results = page.get_by_test_id("no-results")

    def open(self):
        self.page.goto("/products")
        expect(self.cards.first).to_be_visible()  # wait for products to load
        return self

    def search(self, text: str):
        self.search_input.fill(text)
        self.search_button.click()

    def filter_by_category(self, category: str):
        self.category_filter.select_option(category)

    def add_to_cart(self, product_id: int):
        self.page.get_by_test_id(f"add-to-cart-{product_id}").click()

    def product_names(self):
        return self.page.get_by_test_id("product-name").all_text_contents()