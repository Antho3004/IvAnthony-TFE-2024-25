import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';  // Import du Link
import 'bootstrap/dist/css/bootstrap.min.css';

const Inscription = () => {
    const [nomUtilisateur, setNomUtilisateur] = useState('');
    const [email, setEmail] = useState('');
    const [motDePasse, setMotDePasse] = useState('');
    const [erreur, setErreur] = useState('');
    const [succes, setSucces] = useState('');

    const gererInscription = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8080/api/inscription', {
                nom_utilisateur: nomUtilisateur,
                email: email,
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
        <div className="container d-flex justify-content-center align-items-center vh-100">
            <div className="form-container p-4 border rounded shadow-sm bg-light">
                <h2 className="text-center">Inscription</h2>
                <form onSubmit={gererInscription}>
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
                    <button type="submit" className="btn btn-primary w-100">Inscription</button>
                </form>
                {erreur && <p className="text-danger text-center">{erreur}</p>}
                {succes && <p className="text-success text-center">{succes}</p>}
                <p className="text-center mt-3">
                    Vous avez déjà un compte ? <Link to="/connexion">Connectez-vous</Link>
                </p>
            </div>
        </div>
    );
};

export default Inscription;
