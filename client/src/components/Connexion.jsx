import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';  // Import du hook useNavigate

const Connexion = () => {
    const [email, setEmail] = useState('');
    const [motDePasse, setMotDePasse] = useState('');
    const [erreur, setErreur] = useState('');
    const [succes, setSucces] = useState('');
    const navigate = useNavigate();  // Initialisation du hook

    const gererConnexion = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8080/api/connexion', {
                email,
                mot_de_passe: motDePasse,
            });

            // Sauvegarder le token dans le localStorage
            localStorage.setItem('token', response.data.token);
            setSucces(response.data.message);
            setErreur('');

            // Rediriger vers la page calendrier après la connexion réussie
            navigate('/calendrier');
        } catch (err) {
            setErreur(err.response.data.erreur || 'Une erreur est survenue');
            setSucces('');
        }
    };

    return (
        <div className="container d-flex justify-content-center align-items-center vh-100">
            <div className="form-container p-4 border rounded shadow-sm bg-light">
                <h2 className="text-center">Connexion</h2>
                <form onSubmit={gererConnexion}>
                    <div className="mb-3">
                        <input
                            type="email"
                            className="form-control"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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
                {erreur && <p className="text-danger text-center">{erreur}</p>}
                {succes && <p className="text-success text-center">{succes}</p>}
            </div>
        </div>
    );
};

export default Connexion;
