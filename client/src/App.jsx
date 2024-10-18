import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation, useNavigate } from 'react-router-dom';
import { FaCog } from 'react-icons/fa'; // Importer l'icône d'écrou
import Inscription from './components/Inscription';
import Connexion from './components/Connexion';
import Calendrier from './components/calendrier';
import ProtectedRoute from './components/ProctectionRoute';
import 'bootstrap/dist/css/bootstrap.min.css';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  const gererDeconnexion = () => {
    // Supprimer le token du localStorage
    localStorage.removeItem('token');
    // Rediriger vers la page de connexion
    navigate('/connexion');
  };

  return (
    <nav className="navbar navbar-light bg-light">
      <div className="container-fluid">

        {/* Nav links */}
        <div className="d-flex ms-auto">
          {localStorage.getItem('token') ? (
            <>
              <Link to="/parametres" className="navbar-text me-3" style={{ cursor: 'pointer' }}>
                <FaCog size={24} /> {/* l'icône écrou */}
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
          ) : (
            <></>
          )}
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
          <Route path="/calendrier" element={
            <ProtectedRoute>
              <Calendrier />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Connexion />} />
          <Route path="/parametres" element={<div>Page des paramètres</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
