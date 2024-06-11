// Attend que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    // Récupération des éléments du DOM
    var boutonConnexionEleve = document.getElementById('btnConnexionEleve');
    var boutonConnexionFormateurs = document.getElementById('btnConnexionFormateurs');
    var formulaireConnexionEleve = document.getElementById('formulaireConnexionEleve');
    var formulaireConnexionFormateurs = document.getElementById('formulaireConnexionFormateurs');
    var messageErreur = document.getElementById('messageErreur');

    // Fonction pour fermer tous les formulaires et réinitialiser les messages d'erreur
    function fermerTousLesFormulaires() {
        formulaireConnexionEleve.style.display = 'none';
        formulaireConnexionFormateurs.style.display = 'none';
        messageErreur.textContent = ''; // Réinitialiser le message d'erreur général
        document.getElementById('messageErreurEleve').textContent = ''; // Réinitialiser le message d'erreur de l'élève
        document.getElementById('messageErreurFormateur').textContent = ''; // Réinitialiser le message d'erreur du formateur
    }

    // Bouton "Prendre Rendez-vous" : ouvrir le formulaire élève et fermer le formulaire formateur
    boutonConnexionEleve.addEventListener('click', function() {
        fermerTousLesFormulaires();
        formulaireConnexionEleve.style.display = 'block';
    });

    // Bouton "Connexion formateur" : ouvrir le formulaire formateur et fermer le formulaire élève
    boutonConnexionFormateurs.addEventListener('click', function() {
        fermerTousLesFormulaires();
        formulaireConnexionFormateurs.style.display = 'block';
    });

    // Écouter les soumissions de formulaire pour afficher les messages d'erreur
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // Empêcher l'envoi du formulaire par défaut

            var formData = new FormData(form);
            var url = form.getAttribute('action');
            var method = form.getAttribute('method');

            // Envoyer une requête AJAX pour traiter le formulaire
            fetch(url, {
                method: method,
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    // Si la réponse est ok, réinitialiser le formulaire et fermer le formulaire
                    form.reset();
                    fermerTousLesFormulaires();
                } else {
                    // Si la réponse indique une erreur, afficher le message d'erreur dans le formulaire
                    response.json().then(data => {
                        if (form.id === 'formFormateurs') {
                            document.getElementById('messageErreurFormateur').textContent = data.erreur;
                        } else if (form.id === 'formConnexionEleve') {
                            document.getElementById('messageErreurEleve').textContent = data.erreur;
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Erreur lors de la requête AJAX:', error);
            });
        });
    });

    // Fermer les formulaires lorsqu'on clique sur le bouton 'X' et réinitialiser les champs du formulaire
    var fermerBoutons = document.querySelectorAll('.fermer');
    fermerBoutons.forEach(function(bouton) {
        bouton.addEventListener('click', function() {
            this.parentNode.style.display = 'none';
            this.parentNode.reset(); // Réinitialiser les champs du formulaire
        });
    });
});
