document.addEventListener("DOMContentLoaded", function () {
    var calendarEl = document.getElementById("calendar");
    var IdFormateur = calendarEl.dataset.idformateur;
    var selectedStart = null;

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        slotMinTime: "08:00",
        slotMaxTime: "18:30",
        locale: "fr",
        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5],
            startTime: "08:00",
            endTime: "18:00",
        },
        eventClassNames: "disponibilite",
        eventColor: "#35F54F",
        eventTextColor: "#000000",
        events: function (info, successCallback, failureCallback) {
            var disponibilites = [];
            var events = [];

            $.ajax({
                url: "/charger-disponibilite/" + IdFormateur,
                dataType: "json",
                success: function (dispoData) {
                    disponibilites = dispoData.map(function (dispo) {
                        return {
                            start: moment(dispo.start).format(),
                            end: moment(dispo.end).format(),
                            display: dispo.display,
                            color: '#35F54F',
                            id: dispo.id
                        };
                    });

                    $.ajax({
                        url: "/charger-evenements/" + IdFormateur,
                        dataType: "json",
                        success: function (eventData) {
                            events = eventData.map(function (event) {
                                return {
                                    title: event.title,
                                    start: moment(event.start, "YYYY-MM-DDTHH:mm:ss").format(),
                                    end: moment(event.end, "YYYY-MM-DDTHH:mm:ss").format(),
                                    color: "#5EB2F8",
                                    id: event.id,
                                    student: event.student,
                                    title: event.title,
                                    commentaire: event.commentaire,
                                    duree: event.duree
                                };
                            });

                            var allEvents = disponibilites.concat(events);

                            successCallback(allEvents);
                        },
                        error: function (error) {
                            console.error(error);
                            failureCallback(error);
                        },
                    });

                },
                error: function (error) {
                    console.error(error);
                    failureCallback(error);
                },
            });
        },
        selectable: true,
        select: function (info) {
            if (!selectedStart) {
                selectedStart = info.startStr;
            } else {
                var selectedEnd = info.endStr;

                var titre = prompt("Entrez le titre de la disponibilité", "");

                if (titre) {
                    $.ajax({
                        url: '/creer-disponibilite',
                        method: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            datedebut: selectedStart,
                            datefin: selectedEnd,
                            IdFormateur: IdFormateur,
                            titres: titre
                        }),
                        success: function (response) {
                            alert(response.message);
                            calendar.refetchEvents();
                        },
                        error: function (error) {
                            console.error(error);
                            alert('Une erreur s\'est produite lors de la création de la disponibilité.');
                        }
                    });
                }

                selectedStart = null;
            }
        },
        editable: true,
        eventResizable: false,
        eventDrop: function (info) {
            modifier_rendez_vous_par_drag(info.event.id, info.event.startStr, info.event.endStr);
        },
        eventResize: function (info) {
            modifier_rendez_vous_par_resize(info.event.id, info.event.startStr, info.event.endStr);
        },
        eventClick: function (info) {
            var event = info.event;
            var confirmation = confirm("Voulez-vous supprimer ce rendez-vous ?");
            if (confirmation) {
                supprimer_rendez_vous(event.id);
            } else {
                afficher_infos_rendez_vous(event);
            }
        },
        
    });

    calendar.render();

    function afficher_infos_rendez_vous(event) {
        var popupContent = "<p><strong>Élève:</strong> " + event.student + "</p>" +
                           "<p><strong>Titre:</strong> " + event.title + "</p>" +
                           "<p><strong>Commentaire:</strong> " + event.commentaire + "</p>" +
                           "<p><strong>Date:</strong> " + moment(event.start).format("YYYY-MM-DD") + "</p>" +
                           "<p><strong>Durée:</strong> " + event.duree + " minutes</p>" +
                           "<button onclick='supprimer_rendez_vous(" + event.id + ")'>Supprimer</button>";

        $("#rendezvous-info").html(popupContent);
        $("#rendezvous-modal").modal("show");
    }

    function supprimer_rendez_vous(eventId) {
        $.ajax({
            url: '/supprimer-rendez-vous',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id: eventId }),
            success: function (response) {
                alert(response.message);
                calendar.refetchEvents();
            },
            error: function (error) {
                console.error(error);
                alert('Une erreur s\'est produite lors de la suppression du rendez-vous.');
            }
        });
    }

    function modifier_rendez_vous_par_drag(eventId, newStart, newEnd) {
        if (!eventId) {
            console.error("L'identifiant de l'événement n'est pas défini.");
            return;
        }

        $.ajax({
            url: '/modifier-rendez-vous-par-drag',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                id_rendez_vous: eventId,
                new_start: newStart,
                new_end: newEnd
            }),
            success: function (response) {
                alert(response.message);
                calendar.refetchEvents();
            },
            error: function (error) {
                console.error(error);
                alert('Une erreur s\'est produite lors de la modification du rendez-vous.');
            }
        });
    }

    // Dans la fonction chargerDisponibilites() de votre fichier prof.js

function chargerDisponibilites() {
    $.ajax({
        url: "/charger-disponibilite/" + IdFormateur,
        dataType: "json",
        success: function (dispoData) {
            var disponibilitesHtml = '';
            dispoData.forEach(function (dispo) {
                disponibilitesHtml += '<li>' + moment(dispo.start).format('YYYY-MM-DD HH:mm') + ' - ' + moment(dispo.end).format('YYYY-MM-DD HH:mm') + ' <button class="supprimer-dispo-btn" data-id="' + dispo.id + '">Supprimer</button></li>';
            });
            $('#disponibilites').html(disponibilitesHtml);

            // Ajout d'un écouteur d'événements aux boutons de suppression
            $('.supprimer-dispo-btn').click(function() {
                var dispoId = $(this).data('id');
                supprimerDisponibilite(dispoId);
            });
        },
        error: function (error) {
            console.error(error);
        },
    });
}


    // Appel de la fonction pour charger les disponibilités au chargement de la page
    chargerDisponibilites();

    // Fonction pour supprimer une disponibilité
    function supprimerDisponibilite(dispoId) {
        $.ajax({
            url: '/supprimer-disponibilite',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id: dispoId }),
            success: function (response) {
                alert(response.message);
                chargerDisponibilites(); // Recharger la liste des disponibilités après la suppression
            },
            error: function (error) {
                console.error(error);
                alert('Une erreur s\'est produite lors de la suppression de la disponibilité.');
            }
        });
    }

    function modifier_rendez_vous_par_resize(eventId, newStart, newEnd) {
        if (!eventId) {
            console.error("L'identifiant de l'événement n'est pas défini.");
            return;
        }

        $.ajax({
            url: '/modifier-rendez-vous-par-resize',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                id_rendez_vous: eventId,
                new_start: newStart,
                new_end: newEnd
            }),
            success: function (response) {
                alert(response.message);
                calendar.refetchEvents();
            },
            error: function (error) {
                console.error(error);
                alert('Une erreur s\'est produite lors du redimensionnement du rendez-vous.');
            }
        });
    }
});
