from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import mysql.connector
import bcrypt
import jwt
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
            return jsonify({"erreur": "L'adresse mail existe déjà"}), 400

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
@token_requis
def get_calendrier():
    token = request.headers.get('Authorization').split()[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = data.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            id_utilisateur = utilisateur[0]
            cursor.execute("SELECT heure, date FROM type_reveil WHERE id_utilisateur = %s", (id_utilisateur,))
            events = cursor.fetchall()

            # Formater l'heure pour qu'elle s'affiche sous le format "08h30"
            formatted_events = []
            for event in events:
                heure_int = event[0]  # ex: 830 pour 08h30
                date = event[1]

                # Conversion de l'heure au format hhmm (0830) en "08h30"
                heure_str = f"{heure_int:04d}"  # Assurer que l'heure soit toujours à 4 chiffres
                formatted_heure = f"{heure_str[:2]}h{heure_str[2:]}"  # Formater en "hhmm" -> "hhhmm"

                formatted_events.append({
                    "title": formatted_heure,
                    "date": date
                })

            return jsonify({"events": formatted_events}), 200
        else:
            return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la récupération des événements: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/calendrier', methods=['POST'])
@token_requis
def add_calendrier():
    data = request.get_json()
    heure = int(data.get('heure'))  # Stocker l'heure au format entier (par exemple, 0830)
    date = data.get('date')

    if not heure or not date:
        return jsonify({"erreur": "Heure et date requises"}), 400

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Obtenir l'ID de l'utilisateur
        cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            id_utilisateur = utilisateur[0]
            # Insertion de l'heure de réveil dans la base de données
            cursor.execute("INSERT INTO type_reveil (heure, date, id_utilisateur) VALUES (%s, %s, %s)",
                           (heure, date, id_utilisateur))
            connection.commit()

            return jsonify({"message": "Événement ajouté avec succès"}), 201
        else:
            return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de l'ajout de l'événement: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/modifierEvenement', methods=['POST'])
@token_requis
def modifier_evenement():
    data = request.get_json()
    ancienne_date = data.get('ancienneDate')
    ancienne_heure = int(data.get('ancienneHeure'))  # Heure initiale au format entier (par exemple, 0830)
    nouvelle_date = data.get('nouvelleDate')
    nouvelle_heure = int(data.get('nouvelleHeure'))  # Nouvelle heure au format entier

    if not ancienne_date or not ancienne_heure or not nouvelle_date or not nouvelle_heure:
        return jsonify({"erreur": "Données incomplètes"}), 400

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        # Obtenir l'ID de l'utilisateur
        cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            id_utilisateur = utilisateur[0]
            # Mettre à jour l'événement en utilisant la date et l'heure initiales pour l'identifier
            cursor.execute("""
                UPDATE type_reveil 
                SET heure = %s, date = %s 
                WHERE id_utilisateur = %s AND heure = %s AND date = %s
            """, (nouvelle_heure, nouvelle_date, id_utilisateur, ancienne_heure, ancienne_date))
            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({"erreur": "Événement non trouvé"}), 404

            return jsonify({"message": "Événement mis à jour avec succès"}), 200
        else:
            return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la mise à jour de l'événement: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/supprimerEvenement', methods=['POST'])
@token_requis
def supprimer_evenement():
    data = request.get_json()
    date = data.get('date')
    heure = int(data.get('heure'))

    if not date or not heure:
        return jsonify({"erreur": "Heure et date requises"}), 400

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id_utilisateur FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            id_utilisateur = utilisateur[0]
            cursor.execute("DELETE FROM type_reveil WHERE id_utilisateur = %s AND date = %s AND heure = %s",
                           (id_utilisateur, date, heure))
            connection.commit()

            if cursor.rowcount == 0:
                return jsonify({"erreur": "Événement non trouvé"}), 404

            return jsonify({"message": "Événement supprimé avec succès"}), 200
        else:
            return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la suppression de l'événement: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
