// Ajoute un événement de clic pour afficher le formulaire de connexion de l'élève
document.getElementById('btnConnexionEleve').addEventListener('click', function () {
    afficherFormulaire('formulaireConnexionEleve');
    // Efface le message d'erreur précédent
    document.getElementById('erreurIdentifiantEleve').innerText = '';
});

// Ajoute un événement de clic pour afficher le formulaire de connexion des formateurs
document.getElementById('btnConnexionFormateurs').addEventListener('click', function () {
    afficherFormulaire('formulaireFormateurs');
    // Efface le message d'erreur précédent
    document.getElementById('erreurIdentifiantFormateur').innerText = '';
});

// Ajoute un événement de soumission pour le formulaire de connexion des formateurs
document.getElementById('formFormateurs').addEventListener('submit', function (event) {
    event.preventDefault(); // Empêche l'envoi du formulaire par défaut

    // Récupère les valeurs des champs de formulaire
    var pseudo = this.querySelector('[name="Pseudo"]').value;
    var password = this.querySelector('[name="Password"]').value;

    // Envoie une requête AJAX pour vérifier les identifiants côté serveur
    fetch('/login_formateurs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'Pseudo=' + encodeURIComponent(pseudo) + '&Password=' + encodeURIComponent(password),
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // Redirige si le login est réussi
        } else {
            return response.json(); // Retourne la réponse JSON si la redirection n'a pas eu lieu
        }
    })
    .then(data => {
        if (data && data.erreur) {
            // Affiche le message d'erreur
            document.getElementById('erreurIdentifiantFormateur').innerText = data.erreur;
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête AJAX:', error);
    });
});

// Ajoute un événement de soumission pour le formulaire de connexion des élèves
document.getElementById('formConnexionEleve').addEventListener('submit', function (event) {
    event.preventDefault(); // Empêche l'envoi du formulaire par défaut

    // Récupère les valeurs des champs de formulaire
    var pseudo = this.querySelector('[name="PseudoEleve"]').value;
    var password = this.querySelector('[name="PasswordEleve"]').value;

    // Envoie une requête AJAX pour vérifier les identifiants côté serveur
    fetch('/login_eleve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'PseudoEleve=' + encodeURIComponent(pseudo) + '&PasswordEleve=' + encodeURIComponent(password),
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // Redirige si le login est réussi
        } else {
            return response.json(); // Retourne la réponse JSON si la redirection n'a pas eu lieu
        }
    })
    .then(data => {
        if (data && data.erreur) {
            // Affiche le message d'erreur
            document.getElementById('erreurIdentifiantEleve').innerText = data.erreur;
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête AJAX:', error);
    });
});

// Fonction pour afficher le formulaire spécifié
function afficherFormulaire(idFormulaire) {
    var formulaire = document.getElementById(idFormulaire);
    formulaire.style.display = "block"; // Affiche le formulaire
}

// Fonction pour fermer le formulaire spécifié
function fermerFormulaire(idFormulaire) {
    var formulaire = document.getElementById(idFormulaire);
    formulaire.style.display = "none"; // Cache le formulaire
}

// Ajoute un événement de clic pour le bouton d'administration
document.getElementById('btnAdministration').addEventListener('click', function () {
    // Demande le mot de passe pour accéder à l'administration
    var motDePasse = prompt("Veuillez entrer le mot de passe pour accéder à l'administration:");
    if (motDePasse === "6974") {
        window.location.href = "/admin"; // Redirige vers la page d'administration si le mot de passe est correct
    } else {
        alert("Mot de passe incorrect."); // Affiche un message d'erreur si le mot de passe est incorrect
    }
});
