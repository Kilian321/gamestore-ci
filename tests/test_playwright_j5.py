"""
test_playwright_j5.py — TP J5 · Tests UI GameStore
====================================================
Complétez les TODO dans l'ordre.

Lancement :
    pytest tests/test_playwright_j5.py -v --headed
    pytest tests/test_playwright_j5.py -v          # headless (CI)
"""
from playwright.sync_api import Page, expect

from tests.pages.add_game_modal_j5 import AddGameModal
from tests.pages.home_page_j5 import HomePage

BASE_URL = "http://localhost:5000"


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — Tests basiques (sans POM)
# Vous écrivez les sélecteurs directement dans les tests.
# Objectif : comprendre les locators Playwright avant de les encapsuler.
# ══════════════════════════════════════════════════════════════════════════════

def test_page_charge(page: Page):
    page.goto(BASE_URL)
    assert page.title() == "GameStore"
    expect(page.locator("[data-testid=game-list]")).to_be_visible()

def test_liste_jeux_visible(page: Page):
    page.goto(BASE_URL)
    expect(page.locator('[data-testid=game-list]')).to_be_visible()

def test_recherche_filtre_resultats(page: Page):
    page.goto(BASE_URL)

    search_input = page.locator("[data-testid=search-input]")
    search_input.fill("Zelda")

    page.wait_for_timeout(500)

    first_title = page.locator("[data-testid=game-title]").first

    expect(first_title).to_be_visible()

    assert "Zelda" in first_title.inner_text()


def test_filtre_genre_rpg(page: Page):
    page.goto(BASE_URL)
    page.locator("[data-testid=genre-filter]").select_option("RPG")
    cards = page.locator("[data-testid=game-card]")
    expect(cards.first).to_be_visible()

    count = cards.count()

    assert count > 0

    for i in range(count):
        genre = cards.nth(i).locator("[data-testid=game-genre]").inner_text()
        assert "RPG" in genre


# ══════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — Page Object Model
# Mêmes scénarios mais via les classes POM.
# Plus aucun sélecteur dans les tests — tout passe par HomePage / AddGameModal.
# ══════════════════════════════════════════════════════════════════════════════

def test_pom_page_charge(page: Page):
    home = HomePage(page)
    home.navigate()

    assert page.title() == "GameStore"

    expect(home.game_list).to_be_visible()

def test_pom_ajouter_jeu(page: Page):
    home = HomePage(page)
    modal = AddGameModal(page)

    home.navigate()
    home.open_add_form()

    expect(modal.modal).to_be_visible()

    modal.fill_and_submit("Jeu POM Test", "Action", 19.99)

    expect(home.game_list).to_contain_text("Jeu POM Test")

def test_pom_annuler_formulaire(page: Page):
    home = HomePage(page)
    modal = AddGameModal(page)

    home.navigate()
    home.open_add_form()

    expect(modal.modal).to_be_visible()

    modal.cancel()

    expect(modal.modal).not_to_be_visible()

def test_pom_recherche(page: Page):
    home = HomePage(page)

    home.navigate()
    home.search("Zelda")

    first_card = home.get_game_cards().first

    expect(first_card).to_contain_text("Zelda")