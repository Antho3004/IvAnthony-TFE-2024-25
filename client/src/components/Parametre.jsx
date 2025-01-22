import React, { useState } from 'react';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import axios from 'axios';

const Parametres = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [alarmFile, setAlarmFile] = useState(null);
    const [repeatInterval, setRepeatInterval] = useState(5);

    const handleUpdateUser = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.put('http://localhost:8080/api/parametre/utilisateur', {
                username,
                email,
                password,
                newPassword
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            alert('Informations mises à jour avec succès.');
        } catch (error) {
            console.error('Erreur lors de la mise à jour des informations utilisateur:', error);
        }
    };

    const handleDeleteAccount = async () => {
        if (window.confirm('Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.')) {
            try {
                const token = localStorage.getItem('token');
                await axios.delete('http://localhost:8080/api/parametre/utilisateur', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                alert('Compte supprimé avec succès.');
                localStorage.clear();
                window.location.reload();
            } catch (error) {
                console.error('Erreur lors de la suppression du compte:', error);
            }
        }
    };

    const handleUploadAlarm = async (event) => {
        const file = event.target.files[0];
        setAlarmFile(file);

        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const token = localStorage.getItem('token');
                await axios.post('http://localhost:8080/api/parametre/alarme/upload', formData, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                });
                alert('Sonnerie téléchargée avec succès.');
            } catch (error) {
                console.error('Erreur lors du téléchargement de la sonnerie:', error);
            }
        }
    };

    const handleUpdateAlarmSettings = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.put('http://localhost:8080/api/parametre/alarme/settings', {
                repeatInterval
            }, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            alert("Paramètres de l'alarme mis à jour avec succès.");
        } catch (error) {
            console.error("Erreur lors de la mise à jour des paramètres de l'alarme: ", error);
        }
    };

    return (
        <div className="container mt-5">
            <h2>Paramètres</h2>
            <Tabs defaultActiveKey="userInfo" className="mb-3">
                <Tab eventKey="userInfo" title="Informations utilisateur">
                    <Form>
                        <Form.Group className="mb-3" controlId="formUsername">
                            <Form.Label>Nom d'utilisateur</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Entrez votre nom d'utilisateur"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </Form.Group>

                        <Form.Group className="mb-3" controlId="formEmail">
                            <Form.Label>Email</Form.Label>
                            <Form.Control
                                type="email"
                                placeholder="Entrez votre email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </Form.Group>

                        <Form.Group className="mb-3" controlId="formPassword">
                            <Form.Label>Mot de passe actuel</Form.Label>
                            <Form.Control
                                type="password"
                                placeholder="Entrez votre mot de passe actuel"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </Form.Group>

                        <Form.Group className="mb-3" controlId="formNewPassword">
                            <Form.Label>Nouveau mot de passe</Form.Label>
                            <Form.Control
                                type="password"
                                placeholder="Entrez un nouveau mot de passe"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                            />
                        </Form.Group>

                        <Button variant="primary" onClick={handleUpdateUser}>
                            Mettre à jour
                        </Button>
                        <Button variant="danger" className="ms-3" onClick={handleDeleteAccount}>
                            Supprimer le compte
                        </Button>
                    </Form>
                </Tab>

                <Tab eventKey="alarmSettings" title="Paramètres de l'alarme">
                    <Form>
                        <Form.Group className="mb-3" controlId="formAlarmFile">
                            <Form.Label>Importer une sonnerie</Form.Label>
                            <Form.Control
                                type="file"
                                accept="audio/*"
                                onChange={handleUploadAlarm}
                            />
                        </Form.Group>

                        <Form.Group className="mb-3" controlId="formRepeatInterval">
                            <Form.Label>Intervalle de répétition (en minutes)</Form.Label>
                            <Form.Control
                                type="number"
                                min="1"
                                value={repeatInterval}
                                onChange={(e) => setRepeatInterval(e.target.value)}
                            />
                        </Form.Group>

                        <Button variant="primary" onClick={handleUpdateAlarmSettings}>
                            Mettre à jour
                        </Button>
                    </Form>
                </Tab>
            </Tabs>
        </div>
    );
};

export default Parametres;
