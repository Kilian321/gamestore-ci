from playwright.sync_api import Page

BASE_URL = "http://localhost:5000"


class HomePage:

    def __init__(self, page: Page):
        self.page = page

        self.game_list = page.locator('[data-testid=game-list]')
        self.game_count = page.locator('[data-testid=game-count]')
        self.add_btn = page.locator('[data-testid=add-game-btn]')
        self.search_inp = page.locator('[data-testid=search-input]')
        self.genre_sel = page.locator('[data-testid=genre-filter]')

    def navigate(self): self.page.goto('http://localhost:5000')

    def get_game_cards(self): return self.game_list.locator('[data-testid=game-card]')

    def open_add_form(self): self.add_btn.click()

    def search(self, query: str): self.search_inp.fill(query)

    def filter_genre(self, genre: str): self.genre_sel.select_option(genre)