import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Inscription from './components/Inscription';
import Connexion from './components/Connexion';
import 'bootstrap/dist/css/bootstrap.min.css'; // Importer Bootstrap ici

function App() {
  return (
    <Router>
      <div>
        <nav className="navbar navbar-light bg-light"> {/* Navbar avec Bootstrap */}
          <Link className="navbar-brand" to="/inscription">Inscription</Link>
          <Link className="navbar-brand" to="/connexion">Se connecter</Link>
        </nav>

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
