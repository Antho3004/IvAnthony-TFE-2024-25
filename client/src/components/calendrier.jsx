import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import timeGridPlugin from '@fullcalendar/timegrid';
import frLocale from '@fullcalendar/core/locales/fr';
import axios from 'axios';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

const Calendrier = () => {
    const [events, setEvents] = useState([]);
    const [heure, setHeure] = useState('');
    const [date, setDate] = useState('');
    const [eventSelected, setEventSelected] = useState(null);  // Stocker l'événement sélectionné pour modification
    const [newDate, setNewDate] = useState('');
    const [newHeure, setNewHeure] = useState('');

    useEffect(() => {
        const fetchEvents = async () => {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:8080/api/calendrier', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setEvents(response.data.events);
        };
        fetchEvents();
    }, []);

    const handleAddEvent = async () => {
        const token = localStorage.getItem('token');
        try {
            const formattedHeure = heure.replace(':', '');

            await axios.post('http://localhost:8080/api/calendrier', {
                heure: parseInt(formattedHeure),
                date
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setEvents([...events, { title: `${heure.replace(':', 'h')}`, date }]);
        } catch (err) {
            console.error("Erreur lors de l'ajout de l'événement", err);
        }
    };

    const handleEventClick = (clickInfo) => {
        const event = clickInfo.event;
        setEventSelected({
            title: event.title,
            date: event.startStr
        });
        setNewDate(event.startStr);
        setNewHeure(event.title.replace('h', ':'));
    };

    const handleUpdateEvent = async () => {
        const token = localStorage.getItem('token');
        try {
            const formattedHeure = newHeure.replace(':', '');

            await axios.post('http://localhost:8080/api/modifierEvenement', {
                ancienneDate: eventSelected.date,
                ancienneHeure: eventSelected.title.replace('h', ''),
                nouvelleDate: newDate,
                nouvelleHeure: parseInt(formattedHeure),
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const updatedEvents = events.map(event =>
                (event.date === eventSelected.date && event.title === eventSelected.title)
                    ? { ...event, date: newDate, title: newHeure.replace(':', 'h') }
                    : event
            );
            setEvents(updatedEvents);
            setEventSelected(null);
        } catch (err) {
            console.error("Erreur lors de la mise à jour de l'événement", err);
        }
    };

    const handleDeleteEvent = async () => {
        const token = localStorage.getItem('token');
        try {
            await axios.post('http://localhost:8080/api/supprimerEvenement', {
                date: eventSelected.date,
                heure: eventSelected.title.replace('h', ''),
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const filteredEvents = events.filter(event =>
                !(event.date === eventSelected.date && event.title === eventSelected.title)
            );
            setEvents(filteredEvents);
            setEventSelected(null); // Fermer la modale
        } catch (err) {
            console.error("Erreur lors de la suppression de l'événement", err);
        }
    };

    return (
        <div className="container">
            <div className="mb-3">
                <label>Heure de réveil:</label>
                <input
                    type="time"
                    value={heure}
                    onChange={(e) => setHeure(e.target.value)}
                    className="form-control"
                />
                <label>Date:</label>
                <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="form-control"
                />
                <button onClick={handleAddEvent} className="btn btn-primary mt-3">Ajouter</button>
            </div>
            <FullCalendar
                plugins={[dayGridPlugin, interactionPlugin, timeGridPlugin]}
                initialView="dayGridMonth"
                locale={frLocale}
                events={events}
                headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay',
                }}
                buttonText={{
                    today: 'Aujourd\'hui',
                    month: 'Mois',
                    week: 'Semaine',
                    day: 'Jour',
                }}
                eventClick={handleEventClick}
            />

            <Modal show={!!eventSelected} onHide={() => setEventSelected(null)}>
                <Modal.Header closeButton>
                    <Modal.Title>Modifier ou Supprimer l'événement</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>
                        <label>Date:</label>
                        <input
                            type="date"
                            value={newDate}
                            onChange={(e) => setNewDate(e.target.value)}
                            className="form-control"
                        />
                        <label>Heure:</label>
                        <input
                            type="time"
                            value={newHeure}
                            onChange={(e) => setNewHeure(e.target.value)}
                            className="form-control"
                        />
                    </div>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setEventSelected(null)}>
                        Annuler
                    </Button>
                    <Button variant="primary" onClick={handleUpdateEvent}>
                        Enregistrer les modifications
                    </Button>
                    <Button variant="danger" onClick={handleDeleteEvent}>
                        Supprimer
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Calendrier;
