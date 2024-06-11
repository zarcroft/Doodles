// Attend que le DOM soit complètement chargé
document.addEventListener("DOMContentLoaded", function () {
    // Récupération de l'élément du calendrier et de l'ID du formateur
    var calendarEl = document.getElementById("calendar");
    var IdFormateur = calendarEl.dataset.idformateur;

    // Récupérer l'ID de l'élève connecté depuis la session
    var IdEleveConnecte = '';

    // Vérifier si la session contient l'ID de l'élève connecté
    if (sessionStorage.getItem('IdCompteEleve')) {
        IdEleveConnecte = sessionStorage.getItem('IdCompteEleve');
    }

    // Charger les disponibilités du formateur
    $.ajax({
        url: "/charger-disponibilite/" + IdFormateur,
        dataType: "json",
        success: function (dispoData) {
            // Stocker les disponibilités dans la variable disponibilites
            var disponibilites = dispoData.map(function (dispo) {
                return {
                    start: moment(dispo.start).format(),
                    end: moment(dispo.end).format(),
                    display: dispo.display,
                    color: '#35F54F'
                };
            });

            // Définir la fonction isDateAvailable avant de créer le calendrier
            function isDateAvailable(selectedDate) {
                for (let i = 0; i < disponibilites.length; i++) {
                    if (
                        moment(selectedDate).isBetween(disponibilites[i].start, disponibilites[i].end)
                    ) {
                        return true;
                    }
                }
                return false;
            }

            // Charger et traiter les événements
            function loadEvents() {
                // Charger les événements du formateur
                $.ajax({
                    url: "/charger-evenements/" + IdFormateur,
                    dataType: "json",
                    success: function (eventData) {
                        // Traitement des événements
                        var events = eventData.map(function (event) {
                            var eventColor = '#5EB2F8'; // Couleur par défaut pour les événements
                            if (event.IdCompteEleve === IdEleveConnecte) {
                                eventColor = '#F55E5E'; // Couleur différente pour les événements de l'élève connecté
                            }
                            return {
                                title: event.title,
                                start: moment(event.start, "YYYY-MM-DDTHH:mm:ss").format(),
                                end: moment(event.end, "YYYY-MM-DDTHH:mm:ss").format(),
                                duree: event.duree,
                                color: eventColor,
                                Commentaires: event.commentaires,
                                IdCompteEleve: event.IdCompteEleve
                            };
                        });

                        // Fusionner les disponibilités et les événements
                        var allEvents = disponibilites.concat(events);

                        // Rendre le calendrier avec tous les événements
                        renderCalendar(allEvents);
                    },
                    error: function (error) {
                        console.error(error);
                    }
                });
            }

            // Charger les événements une fois que les disponibilités ont été chargées
            loadEvents();

            // Fonction pour afficher la boîte de dialogue
            function showDialog(selectedDate) {
                // Charger le nom et le prénom de l'élève connecté depuis le serveur
                $.ajax({
                    url: '/get-id-eleve',
                    dataType: 'json',
                    success: function (data) {
                        var IdCompteEleve = data.IdCompteEleve;

                        if (IdCompteEleve) {
                            $.ajax({
                                url: '/get-nom-prenom-eleve/' + IdCompteEleve,
                                dataType: 'json',
                                success: function (eleveData) {
                                    var nom = eleveData.Nom;
                                    var prenom = eleveData.Prenom;

                                    var titre = nom + ' ' + prenom;

                                    var startTime = selectedDate.format("HH:mm");
                                    var selectedDateFormat = selectedDate.format("YYYY-MM-DD");

                                    showDialogWithContent(titre, startTime, selectedDateFormat);
                                },
                                error: function (error) {
                                    console.error(error);
                                }
                            });
                        }
                    },
                    error: function (error) {
                        console.error(error);
                    }
                });
            }

            // Fonction pour afficher la boîte de dialogue avec le contenu spécifié
            function showDialogWithContent(titre, heureDebut, selectedDateFormat) {
                var dialogContent = $(
                    '<div class="dialog-content">\
                        <label for="titreInput" class="dialog-label">Titre :</label>\
                        <input type="text" id="titreInput" class="dialog-input" value="' + titre + '" readonly />\
                        <br>\
                        <label for="commentairesInput" class="dialog-label">Commentaires :</label>\
                        <textarea id="commentairesInput" class="dialog-textarea"></textarea>\
                        <br>\
                        <label for="heureDebut" class="dialog-label">Heure de début :</label>\
                        <span id="heureDebut" class="dialog-time">' + heureDebut + '</span>\
                        <br>\
                        <label for="dureeSelect" class="dialog-label">Durée (en minutes) :</label>\
                        <select id="dureeSelect" class="dialog-select"></select>\
                    </div>'
                );

                for (var duration = 30; duration <= 60; duration += 15) {
                    dialogContent.find("#dureeSelect").append('<option value="' + duration + '">' + duration + " minutes</option>");
                }

                dialogContent.dialog({
                    title: "Sélectionnez l'heure de début et la durée",
                    modal: true,
                    buttons: {
                        "Sélectionner": function () {
                            var titre = $("#titreInput").val();
                            var commentaires = $("#commentairesInput").val();
                            var heureDebut = $("#heureDebut").text();
                            var duree = $("#dureeSelect").val();

                            var heureFin = moment(selectedDateFormat + " " + heureDebut)
                                .add(parseInt(duree), 'minutes')
                                .format('HH:mm');

                            $.ajax({
                                url: '/creer-rendez-vous',
                                method: 'POST',
                                contentType: 'application/json',
                                data: JSON.stringify({
                                    debut: selectedDateFormat + ' ' + heureDebut,
                                    fin: selectedDateFormat + ' ' + heureFin,
                                    IdFormateur: IdFormateur,
                                    titre: titre,
                                    Commentaires: commentaires
                                }),
                                success: function (response) {
                                    alert(response.message);
                                    loadEvents();
                                    $(this).dialog("close");
                                },
                                error: function (error) {
                                    console.error(error);
                                    alert('Une erreur s\'est produite lors de la création du rendez-vous.');
                                }
                            });

                            alert('Vous avez choisi le rendez-vous du ' + selectedDateFormat +
                                ' à ' + heureDebut + ' pour une durée de ' + duree + ' minutes.');

                            calendar.unselect();
                        },
                        "Annuler": function () {
                            $(this).dialog("close");
                        }
                    },
                    close: function () {
                        dialogContent.dialog("destroy").remove();
                    }
                });
            }

            // Fonction pour rendre le calendrier
            function renderCalendar(events) {
                var calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: 'timeGridWeek',
                    slotMinTime: "08:00",
                    slotMaxTime: "18:30",
                    locale: 'fr',
                    headerToolbar: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                    },
                    businessHours: {
                        daysOfWeek: [1, 2, 3, 4, 5],
                        startTime: "08:00",
                        endTime: "18:00",
                    },
                    events: events,
                    eventClick: function (info) {
                        var event = info.event;
                        alert('Durée: ' + event.extendedProps.duree + '\nCommentaires: ' + event.extendedProps.Commentaires);
                    },
                    selectable: true,
                    isDateAvailable: isDateAvailable,
                    select: function (info) {
                        var selectedDate = moment(info.start);
                        var isAvailable = isDateAvailable(selectedDate);
                        if (isAvailable) {
                            showDialog(selectedDate);
                        } else {
                            alert("La date " + selectedDate.format("YYYY-MM-DD") + " n'est pas disponible.");
                        }
                    },
                });
                calendar.render();
            }
        },
        error: function (error) {
            console.error(error);
        }
    });
});
