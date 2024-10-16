import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import Inscription from './components/Inscription';
import Connexion from './components/Connexion';
import 'bootstrap/dist/css/bootstrap.min.css';

function Navbar() {
  const location = useLocation();

  return (
    <nav className="navbar navbar-light bg-light">
      <div className="container-fluid justify-content-end"> {/* Utilisation de container-fluid et justify-content-end */}
        {location.pathname === '/inscription' ? (
          <Link className="navbar-brand" to="/connexion">Se connecter</Link>
        ) : (
          <Link className="navbar-brand" to="/inscription">Inscription</Link>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div>
        <Navbar /> {/* Utilisation de la Navbar conditionnelle */}

        <Routes>
          <Route path="/inscription" element={<Inscription />} />
          <Route path="/connexion" element={<Connexion />} />
          <Route path="/" element={<Connexion />} /> {/* Route par défaut */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
