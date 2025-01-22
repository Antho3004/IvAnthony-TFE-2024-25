from flask import Flask, request, jsonify
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
RASPBERRY_API_KEY = os.getenv('RASPBERRY_API_KEY')

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

        # Vérification du header Authorization ou de X-API-KEY
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]  # Enlève "Bearer"
        elif 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']  # Prend la clé API

        if not token:
            return jsonify({"erreur": "Token manquant !"}), 403

        if token == os.getenv('RASPBERRY_API_KEY'):
            # La clé API est valide
            return f(*args, **kwargs)

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
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
    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT heure, date FROM type_reveil")
        events = cursor.fetchall()

        # Formater les événements
        formatted_events = []
        for event in events:
            heure_int = event[0]  # Exemple : 830 pour 08h30
            date = event[1]

            heure_str = f"{heure_int:04d}"  # Assurer 4 chiffres : "0830"
            formatted_heure = f"{heure_str[:2]}:{heure_str[2:]}"  # "0830" -> "08:30"

            # Si `date` est une chaîne, la garder telle quelle, sinon, la formater
            if isinstance(date, str):
                formatted_date = date
            else:
                formatted_date = date.strftime('%Y-%m-%d')

            formatted_events.append({
                "time": formatted_heure,
                "date": formatted_date
            })

        return jsonify({"events": formatted_events}), 200
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

@app.route('/api/parametre/utilisateur', methods=['PUT'])
@token_requis
def update_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    new_password = data.get('newPassword')

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    current_email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT mot_de_passe FROM utilisateurs WHERE email = %s", (current_email,))
        utilisateur = cursor.fetchone()

        if not utilisateur or not bcrypt.checkpw(password.encode('utf-8'), utilisateur[0].encode('utf-8')):
            return jsonify({"erreur": "Mot de passe actuel incorrect"}), 401

        cursor.execute("""
            UPDATE utilisateurs 
            SET nom_utilisateur = %s, email = %s, mot_de_passe = %s 
            WHERE email = %s
        """, (username, email, bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), current_email))
        connection.commit()

        return jsonify({"message": "Informations mises à jour avec succès"}), 200
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la mise à jour des informations: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/parametre/utilisateur', methods=['DELETE'])
@token_requis
def delete_user():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM utilisateurs WHERE email = %s", (email,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"erreur": "Utilisateur non trouvé"}), 404

        return jsonify({"message": "Compte supprimé avec succès"}), 200
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la suppression du compte: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/parametre/alarme/settings', methods=['PUT'])
@token_requis
def update_alarm_settings():
    data = request.get_json()
    repeat_interval = data.get('repeatInterval')

    if not repeat_interval:
        return jsonify({"erreur": "Intervalle de répétition requis"}), 400

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE utilisateurs SET intervalle_repetition = %s WHERE email = %s",
                       (repeat_interval, email))
        connection.commit()

        return jsonify({"message": "Paramètres de l'alarme mis à jour avec succès"}), 200
    except Error as e:
        return jsonify({"erreur": f"Erreur lors de la mise à jour des paramètres: {e}"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/parametre/alarme/upload', methods=['POST'])
@token_requis
def upload_alarm_sound():
    if 'file' not in request.files:
        return jsonify({"erreur": "Fichier manquant"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"erreur": "Nom de fichier invalide"}), 400

    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    email = decoded.get('email')

    try:
        filepath = f"uploads/alarms/{email}_{file.filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

        return jsonify({"message": "Sonnerie téléchargée avec succès", "filepath": filepath}), 201
    except Exception as e:
        return jsonify({"erreur": f"Erreur lors du téléchargement: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
