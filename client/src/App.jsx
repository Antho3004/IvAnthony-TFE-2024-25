import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate, useLocation } from 'react-router-dom';
import { FaCog, FaHome } from 'react-icons/fa'; // Importer l'icône "maison"
import Inscription from './components/Inscription';
import Connexion from './components/Connexion';
import Calendrier from './components/calendrier';
import Parametres from './components/Parametre';
import ProtectedRoute from './components/ProctectionRoute';
import 'bootstrap/dist/css/bootstrap.min.css';

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation(); // Obtenir l'emplacement actuel

  const gererDeconnexion = () => {
    localStorage.removeItem('token');
    navigate('/connexion');
  };

  return (
    <nav className="navbar navbar-light bg-light">
      <div className="container-fluid d-flex align-items-center">
        {/* Afficher le logo "maison" uniquement si l'utilisateur n'est pas sur les pages de connexion ou d'inscription */}
        {location.pathname !== '/connexion' && location.pathname !== '/inscription' && (
          <Link to="/calendrier" className="navbar-brand me-auto" style={{ cursor: 'pointer' }}>
            <FaHome size={24} /> {/* Icône maison */}
          </Link>
        )}

        {/* Nav links */}
        <div className="d-flex">
          {localStorage.getItem('token') ? (
            <>
              <Link to="/parametres" className="navbar-text me-3" style={{ cursor: 'pointer' }}>
                <FaCog size={24} /> {/* Icône engrenage */}
              </Link>

              {/* Bouton de déconnexion */}
              <span
                className="navbar-text text-danger me-3"
                style={{ cursor: 'pointer' }}
                onClick={gererDeconnexion}
              >
                Déconnexion
              </span>
            </>
          ) : null}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div>
        <Navbar /> {/* Navbar conditionnelle */}
        <Routes>
          <Route path="/inscription" element={<Inscription />} />
          <Route path="/connexion" element={<Connexion />} />
          <Route
            path="/calendrier"
            element={
              <ProtectedRoute>
                <Calendrier />
              </ProtectedRoute>
            }
          />
          <Route
            path="/parametres"
            element={
              <ProtectedRoute>
                <Parametres />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Connexion />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
