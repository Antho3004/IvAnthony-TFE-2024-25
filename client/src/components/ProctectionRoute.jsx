import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');

    // Si le token n'existe pas, rediriger vers la page de connexion
    if (!token) {
        return <Navigate to="/connexion" />;
    }

    return children;  // Si le token existe, afficher les enfants
};

export default ProtectedRoute;
