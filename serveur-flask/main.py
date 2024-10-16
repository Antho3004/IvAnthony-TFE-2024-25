from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import mysql.connector
import bcrypt
import jwt  # JSON Web Token library
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from functools import wraps
from mysql.connector import Error

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

# Obtenez la clé secrète depuis l'environnement
SECRET_KEY = os.getenv('SECRET_KEY')

# Configuration de la connexion à la base de données
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='db_tfe'
        )
        print("Connexion à la base de données réussie")
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
    return connection

# Générer un JWT pour l'utilisateur
def generer_jwt(email):
    expiration = datetime.utcnow() + timedelta(hours=2)
    token = jwt.encode({
        'email': email,
        'exp': expiration
    }, SECRET_KEY, algorithm='HS256')
    return token

def token_requis(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]  # Enlève le mot "Bearer"
        if not token:
            return jsonify({"erreur": "Token manquant !"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print("Token validé, données:", data)  # Log des données décodées
        except ExpiredSignatureError:
            return jsonify({"erreur": "Token expiré !"}), 403
        except InvalidTokenError:
            return jsonify({"erreur": "Token invalide !"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/api/inscription', methods=['POST'])
def inscription():
    data = request.get_json()
    nom_utilisateur = data.get('nom_utilisateur')
    email = data.get('email')
    mot_de_passe = data.get('mot_de_passe')

    if not nom_utilisateur or not email or not mot_de_passe:
        return jsonify({"erreur": "Nom d'utilisateur, email et mot de passe requis"}), 400

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            return jsonify({"erreur": "L'utilisateur existe déjà"}), 400

        mot_de_passe_hache = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO utilisateurs (nom_utilisateur, email, mot_de_passe) VALUES (%s, %s, %s)",
                       (nom_utilisateur, email, mot_de_passe_hache.decode('utf-8')))
        connection.commit()
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de l'inscription: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route('/api/connexion', methods=['POST'])
def connexion():
    data = request.get_json()
    email = data.get('email') 
    mot_de_passe = data.get('mot_de_passe')

    if not email or not mot_de_passe:
        return jsonify({"erreur": "Email et mot de passe requis"}), 400

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
    utilisateur = cursor.fetchone()

    cursor.close()
    connection.close()

    if not utilisateur or not bcrypt.checkpw(mot_de_passe.encode('utf-8'), utilisateur[3].encode('utf-8')):
        return jsonify({"erreur": "Email ou mot de passe invalide"}), 401

    # Générer le token JWT
    token = generer_jwt(email)

    return jsonify({"message": "Connexion réussie", "token": token}), 200

@app.route('/api/deconnexion', methods=['POST'])
def deconnexion():
    # Note: Avec JWT, le token est déjà invalidé une fois supprimé du client.
    return jsonify({"message": "Déconnexion réussie"}), 200

@app.route('/api/calendrier', methods=['GET'])
@token_requis  # Appliquer la protection avec le JWT
def calendrier():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id_utilisateur, nom_utilisateur, email FROM utilisateurs")
    utilisateurs = cursor.fetchall()

    cursor.close()
    connection.close()

    utilisateurs_format = [
        {"id_utilisateur": utilisateur[0], "nom_utilisateur": utilisateur[1], "email": utilisateur[2]} 
        for utilisateur in utilisateurs
    ]

    return jsonify(utilisateurs_format), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
