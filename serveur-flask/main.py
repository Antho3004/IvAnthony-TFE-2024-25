from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import bcrypt

app = Flask(__name__)

CORS(app)

# Configuration de la connexion à la base de données
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Par exemple, 'localhost' ou l'adresse IP de votre serveur
            user='root',  # Votre nom d'utilisateur MySQL
            password='root',  # Votre mot de passe MySQL
            database='db_tfe'  # Nom de votre base de données
        )
        print("Connexion à la base de données réussie")
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
    return connection

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

    cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
    utilisateur = cursor.fetchone()

    if utilisateur:
        return jsonify({"erreur": "L'utilisateur existe déjà"}), 400

    # Hachage du mot de passe
    mot_de_passe_hache = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("INSERT INTO utilisateurs (nom_utilisateur, email, mot_de_passe) VALUES (%s, %s, %s)",
                   (nom_utilisateur, email, mot_de_passe_hache.decode('utf-8')))
    connection.commit()
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

    return jsonify({"message": "Connexion réussie"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)
