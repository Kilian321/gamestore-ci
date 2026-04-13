"""
TP1 — Tests Unitaires avec pytest · API GameStore
==================================================
Objectif : écrire 10 tests unitaires couvrant les fonctions de l'API GameStore.
Coverage cible : > 80 %

Lancement :
  pytest test_tp1_unit.py -v --cov=app_gamestore --cov-report=html
"""
from encodings.rot_13 import rot13

import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app_gamestore import app, init_db, get_db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'

    with app.test_client() as c:
        with app.app_context():
            init_db()
            db = get_db()
            db.execute("DELETE FROM games;")
            db.commit()
        yield c


@pytest.fixture
def sample_game():
    return {
        'title': 'The Legend of Zelda: BOTW 2',
        'genre': 'RPG',
        'price': 59.99,
        'rating': 4.9,
        'stock': 100,
    }


# ── Tests à compléter ─────────────────────────────────────────────────────────



class TestListGames:

    def test_get_all_games_returns_200(self, client):
        r = client.get('/games')
        assert r.status_code == 200

    def test_get_all_games_returns_list(self, client):
        r = client.get('/games')
        data = r.get_json()
        assert isinstance(data, list)

    def test_get_games_filter_by_genre(self, client, sample_game):
        r = client.get('/games?genre=RPG')
        data = r.get_json()
        for game in data:
            assert game['genre'] == sample_game['genre']


class TestCreateGame:

    def test_create_valid_game_returns_201(self, client, sample_game):
        r = client.post('/games', json=sample_game)
        assert r.status_code == 201

    def test_create_game_returns_id(self, client, sample_game):
        r = client.post('/games', json=sample_game)
        data = r.get_json()
        assert "id" in data

    def test_create_game_without_title_returns_400(self, client):
        r = client.post('/games', json={
            'genre': 'RPG',
            'price': 59.99,
            'rating': 4.9,
            'stock': 100,
        })
        assert r.status_code == 400

    def test_create_game_with_negative_price_returns_400(self, client):
        r = client.post('/games', json={
            'title': 'The Legend of Zelda: BOTW 2',
            'genre': 'RPG',
            'price': -59.99,
            'rating': 4.9,
            'stock': 100,
        })
        assert r.status_code == 400

    def test_create_duplicate_title_returns_409(self, client, sample_game):
        r1 = client.post('/games', json=sample_game)
        assert r1.status_code == 201

        r2 = client.post('/games', json=sample_game)
        assert r2.status_code == 409

    @pytest.mark.parametrize("title,genre,price,expected_status", [
        ("Zelda", "RPG", 59.99, 201),  # cas valide
        ("", "RPG", 29.99, 400),  # titre vide → erreur
        ("Mario", "RPG", -5.0, 400),  # prix négatif → erreur
        (None, "RPG", 9.99, 400),  # titre absent → erreur
        ("Zelda", "", 9.99, 400),  # Genre obligatoire
        ("Zelda", "RPG", 'a', 400),  # prix doit etre un nombre
    ])
    def test_create_game_validation(self,client, title, genre, price, expected_status):
        r = client.post("/games", json={"title": title, "genre": genre, "price": price})
        assert r.status_code == expected_status

    def test_create_game_without_body(self, client):
        r = client.post("/games")
        assert r.status_code == 400


class TestGetGame:

    def test_get_existing_game_returns_200(self, client, sample_game):
        r1 = client.post('/games', json=sample_game)
        data = r1.get_json()
        game_id = data["id"]

        r2 = client.get(f'/games/{game_id}')
        data_2 = r2.get_json()
        assert data_2["title"] == sample_game["title"]
        assert r2.status_code == 200

    def test_get_nonexistent_game_returns_404(self, client):
        r = client.get('/games/9999')
        assert r.status_code == 404

    def test_get_stats(self, client,sample_game):
        client.post('/games', json=sample_game)

        r = client.get('/games/stats')
        assert r.status_code == 200



class TestDeleteGame:

    def test_delete_existing_game_returns_204(self, client, sample_game):
        r1 = client.post('/games', json=sample_game)
        data = r1.get_json()
        game_id = data["id"]

        r2 = client.delete(f'/games/{game_id}')
        assert r2.status_code == 204

    def test_delete_nonexistent_game_returns_404(self, client):
        r1 = client.delete(f'/games/9999')
        assert r1.status_code == 404

class TestHealthCheck:

    def test_health_check_returns_200(self,client):
        r = client.get('/health')
        assert r.status_code == 200

class TestGetGenre:
    def test_get_genre_returns_200(self, client):
        r = client.get('/genres')
        assert r.status_code == 200

class TestUpdateGame:
    @pytest.mark.parametrize("title,genre,price,expected_status", [
        ("Zelda", "RPG", 59.99, 200),  # cas valide
        ("", "RPG", 29.99, 400),  # titre vide → erreur
        ("Mario", "RPG", -5.0, 400),  # prix négatif → erreur
        (None, "RPG", 9.99, 400),  # titre absent → erreur
        ("Zelda", "", 9.99, 400),  # Genre obligatoire
        ("Zelda", "RPG", 'a', 400),  # prix doit etre un nombre
    ])
    def test_update_game_validation(self, client,sample_game, title, genre, price, expected_status):
        game_id = client.post('/games', json=sample_game).json["id"]
        r = client.put(f"/games/{game_id}", json={"title": title, "genre": genre, "price": price})
        assert r.status_code == expected_status
