import pytest
from main import app, create_connection
import json
from datetime import datetime
import sys
import os
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_setup():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        # Création des tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
            nom_utilisateur VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            mot_de_passe VARCHAR(255)
        )
        """)
        connection.commit()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS type_reveil (
            id_reveil INT AUTO_INCREMENT PRIMARY KEY,
            heure INT,
            date DATE,
            id_utilisateur INT,
            FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
        )
        """)
        connection.commit()
    finally:
        cursor.close()

    yield

def test_integration_signup_login_add_event(client, db_setup):
    # Inscription d'un utilisateur
    signup_data = {
        "nom_utilisateur": "TestUser",
        "email": "test@example.com",
        "mot_de_passe": "password123"
    }
    signup_response = client.post('/api/inscription', data=json.dumps(signup_data), content_type='application/json')
    assert signup_response.status_code == 201
    assert signup_response.get_json()["message"] == "Utilisateur créé avec succès"

    # Connexion pour obtenir un token JWT
    login_data = {"email": "test@example.com", "mot_de_passe": "password123"}
    login_response = client.post('/api/connexion', data=json.dumps(login_data), content_type='application/json')
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    # Ajout d'un événement
    event_data = {
        "heure": 830,
        "date": "2025-01-01"
    }
    event_response = client.post('/api/calendrier',
                                  data=json.dumps(event_data),
                                  headers={"Authorization": f"Bearer {token}"},
                                  content_type='application/json')
    assert event_response.status_code == 201
    assert event_response.get_json()["message"] == "\u00c9v\u00e9nement ajout\u00e9 avec succ\u00e8s"

def test_integration_add_modify_event(client, db_setup):
    # Inscription et connexion
    signup_data = {
        "nom_utilisateur": "TestUser",
        "email": "test@example.com",
        "mot_de_passe": "password123"
    }
    client.post('/api/inscription', data=json.dumps(signup_data), content_type='application/json')
    login_data = {"email": "test@example.com", "mot_de_passe": "password123"}
    login_response = client.post('/api/connexion', data=json.dumps(login_data), content_type='application/json')
    token = login_response.get_json()["token"]

    # Ajout d'un événement
    event_data = {
        "heure": 830,
        "date": "2025-01-01"
    }
    client.post('/api/calendrier',
                data=json.dumps(event_data),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json')

    # Modification de l'événement
    modify_data = {
        "ancienneDate": "2025-01-01",
        "ancienneHeure": 830,
        "nouvelleDate": "2025-01-02",
        "nouvelleHeure": 900
    }
    modify_response = client.post('/api/modifierEvenement',
                                  data=json.dumps(modify_data),
                                  headers={"Authorization": f"Bearer {token}"},
                                  content_type='application/json')
    assert modify_response.status_code == 200
    assert modify_response.get_json()["message"] == "\u00c9v\u00e9nement mis \u00e0 jour avec succ\u00e8s"

def test_integration_add_delete_event(client, db_setup):
    # Inscription et connexion
    signup_data = {
        "nom_utilisateur": "TestUser",
        "email": "test@example.com",
        "mot_de_passe": "password123"
    }
    client.post('/api/inscription', data=json.dumps(signup_data), content_type='application/json')
    login_data = {"email": "test@example.com", "mot_de_passe": "password123"}
    login_response = client.post('/api/connexion', data=json.dumps(login_data), content_type='application/json')
    token = login_response.get_json()["token"]

    # Ajout d'un événement
    event_data = {
        "heure": 830,
        "date": "2025-01-01"
    }
    client.post('/api/calendrier',
                data=json.dumps(event_data),
                headers={"Authorization": f"Bearer {token}"},
                content_type='application/json')

    # Suppression de l'événement
    delete_data = {
        "heure": 830,
        "date": "2025-01-01"
    }
    delete_response = client.post('/api/supprimerEvenement',
                                  data=json.dumps(delete_data),
                                  headers={"Authorization": f"Bearer {token}"},
                                  content_type='application/json')
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "\u00c9v\u00e9nement supprim\u00e9 avec succ\u00e8s"
