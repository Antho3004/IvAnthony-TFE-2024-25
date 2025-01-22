import pytest
from playwright.sync_api import Page
import json

BASE_URL = "http://localhost:8080"  # Assurez-vous que le serveur Flask est bien lancé

def test_e2e_signup_login_add_event_api(page: Page):
    # Inscription via API
    response = page.request.post(f"{BASE_URL}/api/inscription", data=json.dumps({
        "nom_utilisateur": "TestUser",
        "email": "test@example.com",
        "mot_de_passe": "password123"
    }), headers={"Content-Type": "application/json"})
    assert response.status == 201, f"Erreur : {response.text()}"
    assert response.json()["message"] == "Utilisateur créé avec succès"

    # Connexion via API
    response = page.request.post(f"{BASE_URL}/api/connexion", data=json.dumps({
        "email": "test@example.com",
        "mot_de_passe": "password123"
    }), headers={"Content-Type": "application/json"})
    assert response.status == 200, f"Erreur : {response.text()}"
    token = response.json()["token"]

    # Ajout d'un événement via API
    response = page.request.post(f"{BASE_URL}/api/calendrier", data=json.dumps({
        "heure": 830,
        "date": "2025-01-01"
    }), headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    assert response.status == 201, f"Erreur : {response.text()}"
    assert response.json()["message"] == "Événement ajouté avec succès"
