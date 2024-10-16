from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Mock de stockage d'utilisateur (pour le moment on n'utilise pas de base de données)
utilisateurs = {
    "testuser": {
        "mot_de_passe": "123"
    }
}

@app.route('/api/inscription', methods=['POST'])
def inscription():
    data = request.get_json()
    nom_utilisateur = data.get('nom_utilisateur')
    mot_de_passe = data.get('mot_de_passe')

    if not nom_utilisateur or not mot_de_passe:
        return jsonify({"erreur": "Nom d'utilisateur et mot de passe requis"}), 400

    if nom_utilisateur in utilisateurs:
        return jsonify({"erreur": "L'utilisateur existe déjà"}), 400

    utilisateurs[nom_utilisateur] = {"mot_de_passe": mot_de_passe}
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route('/api/connexion', methods=['POST'])
def connexion():
    data = request.get_json()
    nom_utilisateur = data.get('nom_utilisateur')
    mot_de_passe = data.get('mot_de_passe')

    if not nom_utilisateur or not mot_de_passe:
        return jsonify({"erreur": "Nom d'utilisateur et mot de passe requis"}), 400

    utilisateur = utilisateurs.get(nom_utilisateur)

    if not utilisateur or utilisateur['mot_de_passe'] != mot_de_passe:
        return jsonify({"erreur": "Nom d'utilisateur ou mot de passe invalide"}), 401

    return jsonify({"message": "Connexion réussie"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)

