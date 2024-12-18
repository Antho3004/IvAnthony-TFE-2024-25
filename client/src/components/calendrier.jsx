import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import timeGridPlugin from '@fullcalendar/timegrid';
import frLocale from '@fullcalendar/core/locales/fr';
import axios from 'axios';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import moment from 'moment';

const Calendrier = () => {
    const [events, setEvents] = useState([]);
    const [heure, setHeure] = useState('');
    const [date, setDate] = useState('');
    const [eventSelected, setEventSelected] = useState(null);
    const [newDate, setNewDate] = useState('');
    const [newHeure, setNewHeure] = useState('');
    const [optionSelectionnee, setOptionSelectionnee] = useState(null);
    const [joursSelectionnes, setJoursSelectionnes] = useState([]);
    const [intervalleDate, setIntervalleDate] = useState({ debut: '', fin: '' });
    const [nombreSemaines, setNombreSemaines] = useState(1);
    const [dateDebut, setDateDebut] = useState('');
    const [dateSonnerUneFois, setDateSonnerUneFois] = useState('');  // État pour la date de "sonner une fois"

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

    const joursMap = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche"
    };

    const handleAddEvent = async () => {
        const token = localStorage.getItem('token');
        const formattedHeure = heure.replace(':', '');
        let newEvents = [];

        try {
            if (optionSelectionnee === 'personnaliser') {
                if (joursSelectionnes.length > 0 && nombreSemaines) {
                    // Gestion des jours répétés
                    const startDate = moment(dateDebut);
                    const totalDays = nombreSemaines * 7;

                    for (let i = 0; i < totalDays; i++) {
                        const currentDate = startDate.clone().add(i, 'days');
                        const dayNameEnglish = currentDate.format('dddd');
                        const dayNameFrench = joursMap[dayNameEnglish];

                        if (joursSelectionnes.includes(dayNameFrench)) {
                            const formattedDate = currentDate.format('YYYY-MM-DD');

                            await axios.post('http://localhost:8080/api/calendrier', {
                                heure: parseInt(formattedHeure),
                                date: formattedDate
                            }, {
                                headers: { 'Authorization': `Bearer ${token}` }
                            });

                            newEvents.push({ title: `${heure.replace(':', 'h')}`, date: formattedDate });
                        }
                    }
                } else if (intervalleDate.debut && intervalleDate.fin) {
                    // Gestion de la plage de dates
                    const startDate = moment(intervalleDate.debut);
                    const endDate = moment(intervalleDate.fin);

                    if (startDate.isAfter(endDate)) {
                        alert("La date de début doit être avant la date de fin.");
                        return;
                    }

                    const dates = [];
                    for (let date = startDate.clone(); date.isSameOrBefore(endDate); date.add(1, 'days')) {
                        dates.push(date.format('YYYY-MM-DD'));
                    }

                    for (const date of dates) {
                        await axios.post('http://localhost:8080/api/calendrier', {
                            heure: parseInt(formattedHeure),
                            date
                        }, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });

                        newEvents.push({ title: `${heure.replace(':', 'h')}`, date });
                    }
                } else {
                    alert("Veuillez compléter tous les champs nécessaires pour l'option sélectionnée.");
                    return;
                }
            } else if (optionSelectionnee === 'sonnerUneFois' && dateSonnerUneFois) {
                // Gestion de l'option "Sonner une fois"
                const formattedDate = moment(dateSonnerUneFois).format('YYYY-MM-DD');
                await axios.post('http://localhost:8080/api/calendrier', {
                    heure: parseInt(formattedHeure),
                    date: formattedDate
                }, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                newEvents.push({ title: `${heure.replace(':', 'h')}`, date: formattedDate });
            } else {
                alert("Veuillez sélectionner une date pour l'option 'Sonner une fois'.");
                return;
            }

            setEvents([...events, ...newEvents]);

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
            const formattedHeure = newHeure.replace(':', 'h');  // Remplacez ":" par "h" pour respecter le format attendu.

            await axios.post('http://localhost:8080/api/modifierEvenement', {
                ancienneDate: eventSelected.date,
                ancienneHeure: eventSelected.title.replace('h', ''),
                nouvelleDate: newDate,
                nouvelleHeure: parseInt(newHeure.replace(':', '')),
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const updatedEvents = events.map(event =>
                (event.date === eventSelected.date && event.title === eventSelected.title)
                    ? { ...event, date: newDate, title: formattedHeure } // Assurez-vous que la nouvelle heure est au format "hh:mm"
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
            setEventSelected(null);
        } catch (err) {
            console.error("Erreur lors de la suppression de l'événement", err);
        }
    };

    const activerOption = (option) => {
        setOptionSelectionnee(option);
        setDate('');  // Réinitialisation de la date pour chaque option
        setJoursSelectionnes([]);
        setIntervalleDate({ debut: '', fin: '' });
        setDateDebut('');
        setNombreSemaines(1);
        setDateSonnerUneFois('');  // Réinitialisation de la date "Sonner une fois"
    };

    return (
        <div className="container">
            <div className="mb-3">
                <label>Heure de réveil:</label>
                <input
                    type="time"
                    value={heure}
                    onChange={(e) => setHeure(e.target.value)}
                    className="form-control mb-3"
                    style={{ maxWidth: '200px' }}
                />

                <div className="d-flex mb-3">
                    <button
                        className={`btn ${optionSelectionnee === 'sonnerUneFois' ? 'btn-primary' : 'btn-outline-primary'} me-2`}
                        onClick={() => activerOption('sonnerUneFois')}
                    >
                        Sonner une fois
                    </button>
                    <button
                        className={`btn ${optionSelectionnee === 'personnaliser' ? 'btn-primary' : 'btn-outline-primary'}`}
                        onClick={() => activerOption('personnaliser')}
                    >
                        Personnaliser
                    </button>
                </div>

                {optionSelectionnee === 'personnaliser' && (
                    <>
                        {/* Champs pour la personnalisation des jours */}
                        <div className="mb-3">
                            <label>Jours de répétition:</label>
                            <div className="d-flex flex-wrap">
                                {['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'].map((jour) => (
                                    <button
                                        key={jour}
                                        className={`btn ${joursSelectionnes.includes(jour) ? 'btn-success' : 'btn-outline-success'} me-2 mb-2`}
                                        onClick={() => setJoursSelectionnes((prev) =>
                                            prev.includes(jour)
                                                ? prev.filter((j) => j !== jour)
                                                : [...prev, jour]
                                        )}
                                    >
                                        {jour}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="mb-3">
                            <label>Date de début:</label>
                            <input
                                type="date"
                                value={dateDebut}
                                onChange={(e) => setDateDebut(e.target.value)}
                                className="form-control mb-3"
                            />
                        </div>

                        <div className="mb-3">
                            <label>Nombre de semaines:</label>
                            <input
                                type="number"
                                value={nombreSemaines}
                                onChange={(e) => setNombreSemaines(e.target.value)}
                                className="form-control mb-3"
                            />
                        </div>

                        <div className="mb-3">
                            <label>Plage de dates (Du/Au):</label>
                            <div className="d-flex">
                                <input
                                    type="date"
                                    value={intervalleDate.debut}
                                    onChange={(e) => setIntervalleDate({ ...intervalleDate, debut: e.target.value })}
                                    className="form-control mb-3 me-2"
                                />
                                <input
                                    type="date"
                                    value={intervalleDate.fin}
                                    onChange={(e) => setIntervalleDate({ ...intervalleDate, fin: e.target.value })}
                                    className="form-control mb-3"
                                />
                            </div>
                        </div>
                    </>
                )}

                {optionSelectionnee === 'sonnerUneFois' && (
                    <div className="mb-3">
                        <label>Date spécifique:</label>
                        <input
                            type="date"
                            value={dateSonnerUneFois}
                            onChange={(e) => setDateSonnerUneFois(e.target.value)}
                            className="form-control mb-3"
                        />
                    </div>
                )}
            </div>

            <button onClick={handleAddEvent} className="btn btn-success">Ajouter événement</button>

            <FullCalendar
                plugins={[dayGridPlugin, interactionPlugin, timeGridPlugin]}
                locale={frLocale}
                events={events}
                eventClick={handleEventClick}
            />

            {/* Modal de mise à jour d'événement */}
            <Modal show={eventSelected !== null} onHide={() => setEventSelected(null)}>
                <Modal.Header closeButton>
                    <Modal.Title>Modifier l'événement</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>
                        <label>Date:</label>
                        <input
                            type="date"  // Remplacez "datetime-local" par "date"
                            value={newDate}
                            onChange={(e) => setNewDate(e.target.value)}
                            className="form-control"
                        />
                    </div>
                    <div>
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
                        Mettre à jour
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
