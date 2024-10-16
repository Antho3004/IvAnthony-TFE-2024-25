import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

const Connexion = () => {
    const [nomUtilisateur, setNomUtilisateur] = useState('');
    const [motDePasse, setMotDePasse] = useState('');
    const [erreur, setErreur] = useState('');
    const [succes, setSucces] = useState('');

    const gererConnexion = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8080/api/connexion', {
                nom_utilisateur: nomUtilisateur,
                mot_de_passe: motDePasse,
            });
            setSucces(response.data.message);
            setErreur('');
        } catch (err) {
            setErreur(err.response.data.erreur || 'Une erreur est survenue');
            setSucces('');
        }
    };

    return (
        <div className="container d-flex justify-content-center align-items-center vh-100"> {/* Centrer le conteneur */}
            <div className="form-container p-4 border rounded shadow-sm bg-light"> {/* Formulaire avec Bootstrap */}
                <h2>Connexion</h2>
                <form onSubmit={gererConnexion}>
                    <div className="mb-3">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Nom d'utilisateur"
                            value={nomUtilisateur}
                            onChange={(e) => setNomUtilisateur(e.target.value)}
                        />
                    </div>
                    <div className="mb-3">
                        <input
                            type="password"
                            className="form-control"
                            placeholder="Mot de passe"
                            value={motDePasse}
                            onChange={(e) => setMotDePasse(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">Se connecter</button>
                </form>
                {erreur && <p className="text-danger">{erreur}</p>}
                {succes && <p className="text-success">{succes}</p>}
            </div>
        </div>
    );
};

export default Connexion;
