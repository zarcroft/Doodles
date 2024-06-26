from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_socketio import SocketIO
import pymysql
from flask_session import Session
from datetime import datetime, timedelta
import json
import bcrypt
from bcrypt import checkpw, hashpw, gensalt
from flask_mail import Mail, Message
from flask import flash



app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app)

db = pymysql.connect(host='127.0.0.1',
                     user='doodle',
                     password='doodle',
                     database='doodle',
                     cursorclass=pymysql.cursors.DictCursor)

app.config.update( MAIL_SERVER="smtp.gmail.com",
                   MAIL_PORT=465, MAIL_USE_SSL="MAIL_USE_SSL",
                   MAIL_USERNAME="yoancourspromeo@gmail.com",
                   MAIL_PASSWORD="oehfwyycnrbaxows",
                   )
mail = Mail(app)

# Fonction pour récupérer les classes depuis la base de données
def get_classe():
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM Classe')
        classe = cursor.fetchall()
    return classe

# Fonction pour récupérer les formateurs par classe depuis la base de données
def get_formateurs_par_classe(idclasse):
    with db.cursor() as cursor:
        cursor.execute('''
            SELECT f.IdFormateur, f.Nom, f.Prenom
            FROM Formateur f
            INNER JOIN formation fc ON f.IdFormateur = fc.IdFormateur
            WHERE fc.IDClasse = %s
        ''', (idclasse,))
        formateurs = cursor.fetchall()
    return formateurs

@app.route('/')
def index():
    return render_template('index.html')

# Route pour la connexion des formateurs
@app.route('/login_formateurs', methods=['POST'])
def login_formateurs():
    pseudo = request.form.get('Pseudo')
    mot_de_passe = request.form.get('Password')

    if not pseudo or not mot_de_passe:
        return jsonify({'erreur': 'Veuillez fournir un pseudo et un mot de passe'}), 400

    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM CompteFormateur WHERE Pseudo=%s AND MotDePasse=%s', (pseudo, mot_de_passe))
        utilisateur = cursor.fetchone()

    if utilisateur:
        session['IdFormateur'] = str(utilisateur['IdFormateur'])
        session['logged_in'] = True  # Ajouter cette ligne
        return redirect(url_for('prof', pseudo=pseudo))
    else:
        return jsonify({'erreur': 'Identifiants incorrects'}), 401


@app.route('/login_eleve', methods=['POST'])
def login_eleve():
    pseudo = request.form.get('PseudoEleve')
    mot_de_passe = request.form.get('PasswordEleve')

    if not pseudo or not mot_de_passe:
        return jsonify({'erreur': 'Veuillez fournir un pseudo et un mot de passe'}), 400

    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM compteeleve WHERE Pseudo=%s AND MotDePasse=%s', (pseudo, mot_de_passe))
        utilisateur = cursor.fetchone()

    if utilisateur:
        session['IdCompteEleve'] = str(utilisateur['IdEleve'])
        session['logged_in'] = True
        return redirect(url_for('afficher_formateurs'))
    else:
        return jsonify({'erreur': 'Identifiants incorrects'}), 401



@app.route('/logout')
def logout():
    session.clear()
    session.pop('IdFormateur', None)
    session.pop('IdCompteEleve', None)
    session.pop('logged_in', None)  # Ajouter cette ligne
    
    return redirect(url_for('index'))


# Route pour afficher le profil du formateur
@app.route('/prof/<pseudo>')
def prof(pseudo):
    # Récupérer l'IdFormateur depuis la session
    IdFormateur = session.get('IdFormateur')

    if not IdFormateur:
        return redirect(url_for('index'))  # Rediriger vers la page d'accueil si l'utilisateur n'est pas connecté

    with db.cursor() as cursor:
        cursor.execute('''
            SELECT cu.Pseudo, f.Nom, f.Prenom, f.IdFormateur
            FROM CompteFormateur cu
            JOIN Formateur f ON cu.IdFormateur = f.IdFormateur
            WHERE cu.Pseudo = %s
        ''', (pseudo,))
        formateur = cursor.fetchone()

    if formateur:
        return render_template('prof.html', formateur=formateur, IdFormateur=IdFormateur)
    else:
        return "Utilisateur non trouvé"

# Route pour afficher le planning du formateur
from flask import render_template

@app.route('/planning-prof/<IdFormateur>')
def planning_prof(IdFormateur):
    # Récupérer l'IdCompteEleve depuis la session
    IdCompteEleve = session.get('IdCompteEleve')

    if not IdCompteEleve:
        return redirect(url_for('index'))  # Rediriger vers la page d'accueil si l'élève n'est pas connecté

    IdFormateur = int(IdFormateur)

    # Utiliser l'IdFormateur pour récupérer les informations nécessaires depuis la base de données
    with db.cursor() as cursor:
        # Récupérer les informations du formateur
        cursor.execute('''
            SELECT IdFormateur, Nom, Prenom
            FROM Formateur
            WHERE IdFormateur = %s
        ''', (IdFormateur,))
        formateur = cursor.fetchone()

        # Récupérer les disponibilités du formateur
        cursor.execute('''
            SELECT IdReservation, HeureDebut, HeureFin
            FROM Reservation
            WHERE IdFormateur = %s
        ''', (IdFormateur,))
        reservations = cursor.fetchall()

        disponibilites = []
        for reservation in reservations:
            disponibilites.append({
                'title': 'Disponibilité',
                'start': f"{reservation['HeureDebut']}",
                'end': f"{reservation['HeureFin']}"
            })

        # Récupérer le nom et le prénom de l'élève connecté
        cursor.execute('''
            SELECT e.Nom, e.Prenom
            FROM CompteEleve ce
            INNER JOIN Eleve e ON ce.IdEleve = e.IdEleve
            WHERE ce.IdCompteEleve = %s
        ''', (IdCompteEleve,))
        eleve_data = cursor.fetchone()
        nom_eleve = eleve_data['Nom']
        prenom_eleve = eleve_data['Prenom']

    return render_template('planning_prof.html', formateur=formateur, disponibilites=disponibilites, nom_eleve=nom_eleve, prenom_eleve=prenom_eleve)

# Route pour la connexion des élèves
# Route pour la connexion des élèves


# Route pour afficher les formateurs
@app.route('/afficher_formateurs')
def afficher_formateurs():
    # Récupérer l'IdEleve depuis la session
    id_eleve = session.get('IdCompteEleve')

    if not id_eleve:
        flash('Vous devez être connecté pour accéder à cette page.', 'danger')
        return redirect(url_for('index'))

    # 1. Récupérer l'ID de la classe de l'élève
    with db.cursor() as cursor:
        cursor.execute('SELECT IDClasse FROM eleve WHERE IdEleve = %s', (id_eleve,))
        result = cursor.fetchone()

        if result:
            id_classe = result['IDClasse']
        else:
            flash('Classe non trouvée pour cet élève.', 'danger')
            return redirect(url_for('index'))

        # 2. Récupérer les formateurs associés à la classe de l'élève
        formateurs = get_formateurs_par_classe(id_classe)

    # 3. Afficher la liste des formateurs dans le template
    return render_template('afficher_formateurs.html', formateurs=formateurs)



@app.route('/creer-rendez-vous', methods=['POST'])
def creer_rendez_vous():
    data = request.get_json()

    debut = data['debut']
    fin = data['fin']
    IdFormateur = data['IdFormateur']
    
    IdCompteEleve = session.get('IdCompteEleve')

    if IdCompteEleve is None:
        return jsonify({'erreur': 'L\'utilisateur n\'est pas correctement connecté'}), 401
    
    Commentaires = data.get('Commentaires')
    with db.cursor() as cursor:
        cursor.execute('SELECT Nom, Prenom FROM eleve WHERE IdEleve = %s', (IdCompteEleve,))
        eleve = cursor.fetchone()
        if not eleve:
            return jsonify({'erreur': 'Impossible de trouver l\'élève'}), 404

    # Utiliser le nom et le prénom de l'élève pour créer le titre du rendez-vous
    titre = f"{eleve['Nom']} {eleve['Prenom']}"
   
    # Enregistrement dans la base de données
    with db.cursor() as cursor:
        cursor.execute('''
            INSERT INTO reservation (HeureDebut, HeureFin, IdFormateur, IdCompteEleve, Titres, Commentaires)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (debut, fin, IdFormateur, IdCompteEleve, titre, Commentaires))

    db.commit()

    formateur_Email = get_formateur_Email(IdFormateur)
    if formateur_Email:
        send_Email_to_formateur(formateur_Email, debut, fin, titre, Commentaires)

    return jsonify({'message': 'Rendez-vous créé avec succès'})

@app.route('/get-nom-prenom-eleve/<IdCompteEleve>')
def get_nom_prenom_eleve(IdCompteEleve):
    with db.cursor() as cursor:
        cursor.execute('SELECT Nom, Prenom FROM eleve WHERE IdEleve = %s', (IdCompteEleve,))
        eleve = cursor.fetchone()
        if eleve:
            return jsonify({'Nom': eleve['Nom'], 'Prenom': eleve['Prenom']})
        else:
            return jsonify({'erreur': 'Élève non trouvé'}), 404

def get_formateur_Email(IdFormateur):
    with db.cursor() as cursor:
        cursor.execute('SELECT Email FROM formateur WHERE IdFormateur = %s', (IdFormateur,))
        formateur = cursor.fetchone()
        if formateur:
            return formateur['Email']
        else:
            return None

def send_Email_to_formateur(formateur_Email, debut, fin, titre, Commentaires):
    msg = Message(subject='Nouveau rendez-vous créé',
                  sender='flaskdoodle60@gmail.com',
                  recipients=[formateur_Email],
                  body=f'Un nouveau rendez-vous a été créé avec les détails suivants:\n\n'
                       f'Début: {debut}\n'
                       f'Fin: {fin}\n'
                       f'Nom Prénom: {titre}\n\n'
                       f'Commentaires: {Commentaires}\n\n'
                       f'Merci.')

    mail.send(msg)


if __name__ == "__main__":
    socketio.run(app)

@app.route('/charger-evenements/<IdFormateur>')
def charger_evenements(IdFormateur):
    IdFormateur = int(IdFormateur)

    with db.cursor() as cursor:
        cursor.execute('''
            SELECT IdReservation, HeureDebut, HeureFin,  Titres, Commentaires
            FROM reservation
            WHERE IdFormateur = %s
        ''', (IdFormateur,))
        evenements = cursor.fetchall()

    evenements_list = []
    for evenement in evenements:
        id_event = evenement['IdReservation']  
        start_time = evenement['HeureDebut']
        end_time = evenement['HeureFin']

        evenements_list.append({
            'id': id_event,  
            'title': f"{evenement['Titres']}",
            'start': f"{start_time}",
            'end': f"{end_time}",          
        })

    return jsonify(evenements_list)

@app.route('/get-id-eleve')
def get_id_eleve():
    IdEleve = session.get('IdCompteEleve')
    return jsonify({'IdCompteEleve': IdEleve})

@app.route('/creer-disponibilite', methods=['POST'])
def creer_disponibilite():
    data = request.get_json()

    datedebut = data['datedebut']
    datefin = data['datefin']
    IdFormateur = data['IdFormateur']
    titres = data['titres']
   
    with db.cursor() as cursor:
        cursor.execute('''
        INSERT INTO disponibilite (DateDebut, DateFin, IdFormateur, Titres)
        VALUES (%s, %s, %s, %s)
    ''', (datedebut, datefin, IdFormateur, titres))

    db.commit()

    return jsonify({'message': 'Disponibilité créée avec succès'})

@app.route('/charger-disponibilite/<IdFormateur>')
def charger_disponibilite(IdFormateur):
    IdFormateur = int(IdFormateur)

    with db.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM disponibilite
            WHERE IdFormateur = %s
        ''', (IdFormateur,))
        disponibilites = cursor.fetchall()

    disponibilites_list = []
    for disponibilite in disponibilites:
        disponibilites_list.append({
        'id' : disponibilite['IdDisponibilite'],
        'start': disponibilite['DateDebut'].strftime('%Y-%m-%dT%H:%M:%S'),
        'end': disponibilite['DateFin'].strftime('%Y-%m-%dT%H:%M:%S'),
        'display': 'background'
    })

    return jsonify(disponibilites_list)

@app.route('/supprimer-disponibilite', methods=['POST'])
def supprimer_disponibilite():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Ajouter un log pour voir les données reçues
        if not data or 'id' not in data:
            return jsonify({'message': 'Invalid request: ID is missing'}), 400

        id = data['id']
        print(f"Deleting availability with ID: {id}")  # Log de l'ID à supprimer
        
        with db.cursor() as cursor:
            cursor.execute('DELETE FROM disponibilite WHERE IdDisponibilite = %s', (id,))
        
        db.commit()
        
        return jsonify({'message': 'Disponibilité supprimée avec succès'})
    except Exception as e:
        print(f"Error: {e}")  # Log de l'erreur
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/modifier-disponibilite', methods=['POST'])
def modifier_disponibilite():
    data = request.get_json()
    id = data['id']
    new_start = data['new_start']
    new_end = data['new_end']
    
    with db.cursor() as cursor:
        cursor.execute('''
            UPDATE disponibilite
            SET DateDebut = %s, DateFin = %s
            WHERE IdDisponibilite = %s
        ''', (new_start, new_end, id))
    
    db.commit()
    
    return jsonify({'message': 'Disponibilité modifiée avec succès'})


# Route pour supprimer un rendez-vous
@app.route('/supprimer-rendez-vous', methods=['POST'])
def supprimer_rendez_vous():
    data = request.get_json()

    id_rendez_vous = data['id']

    with db.cursor() as cursor:
        cursor.execute('DELETE FROM reservation WHERE IdReservation = %s', (id_rendez_vous,))
    
    db.commit()

    return jsonify({'message': 'Le rendez-vous a été supprimé avec succès'})




@app.route('/modifier-rendez-vous-par-drag', methods=['POST'])
def modifier_rendez_vous_par_drag():
    data = request.get_json()

    # Extraire les données envoyées depuis le client
    id_rendez_vous = data['id_rendez_vous']
    new_start = data['new_start']
    new_end = data['new_end']

    try:
        # Mettre à jour le rendez-vous dans la base de données
        with db.cursor() as cursor:
            cursor.execute('''
                UPDATE reservation
                SET HeureDebut = %s, HeureFin = %s
                WHERE IdReservation = %s
            ''', (new_start, new_end,  id_rendez_vous))
        
        # Valider les modifications dans la base de données
        db.commit()

        # Retourner une réponse JSON indiquant que la modification a été effectuée avec succès
        return jsonify({'message': 'Le rendez-vous a été modifié avec succès'})
    except Exception as e:
        # En cas d'erreur, imprimer le message d'erreur
        print("Erreur lors de la mise à jour du rendez-vous:", e)
        # Retourner un message d'erreur au client
        return jsonify({'erreur': 'Une erreur s\'est produite lors de la modification du rendez-vous. Veuillez réessayer.'}), 500

@app.route('/propos')
def propos():
    return render_template('propos.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/create')
def create():
    return render_template('admin/create.html')

@app.route('/delete')
def delete():
    return render_template('admin/delete.html')

# Routes pour accéder aux différentes pages de création
@app.route('/create/eleve')
def create_eleve():
    with db.cursor() as cursor:
        cursor.execute('SELECT IDClasse, Classe FROM Classe')
        classes = cursor.fetchall()
    return render_template('admin/create/create-eleve.html', classes=classes)

@app.route('/cree-compte-formateur', methods=['GET', 'POST'])
def create_compte_formateur():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        mot_de_passe = request.form['mot_de_passe']
        id_formateur = request.form['id_formateur']

        # Insérer les données du compte formateur dans la base de données
        with db.cursor() as cursor:
            try:
                cursor.execute('INSERT INTO CompteFormateur (Pseudo, MotDePasse, IdFormateur) VALUES (%s, %s, %s)', (pseudo, mot_de_passe, id_formateur))
                db.commit()
                # Afficher un message de succès
                flash('Compte formateur créé avec succès', 'success')
            except Exception as e:
                # Afficher un message d'échec en cas d'erreur lors de l'insertion dans la base de données
                flash('Erreur lors de la création du compte formateur', 'danger')

        # Rediriger vers la même page pour afficher les messages flash
        return redirect(url_for('create_formateur'))

    else:
        # Afficher le formulaire de création de compte formateur
        with db.cursor() as cursor:
            cursor.execute('SELECT IdFormateur, Nom, Prenom FROM formateur')
            formateurs = cursor.fetchall()

        return render_template('admin/create/create-compte-formateur.html', formateurs=formateurs)

@app.route('/create/compte-formateur')
def create_formateur():
    with db.cursor() as cursor:
        cursor.execute('SELECT IdFormateur, Nom, Prenom FROM formateur')
        formateurs = cursor.fetchall()

    return render_template('admin/create/create-formateur.html', formateurs=formateurs)

@app.route('/create/compte-eleve', methods=['GET', 'POST'])
def create_compte_eleve():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        mot_de_passe = request.form['mot_de_passe']
        id_eleve = request.form['id_eleve']

        # Insérer les données du compte élève dans la base de données
        with db.cursor() as cursor:
            try:
                cursor.execute('INSERT INTO compteeleve (Pseudo, MotDePasse, IdEleve) VALUES (%s, %s, %s)', (pseudo, mot_de_passe, id_eleve))
                db.commit()
                # Afficher un message de succès
                flash('Compte élève créé avec succès', 'success')
            except Exception as e:
                # Afficher un message d'échec en cas d'erreur lors de l'insertion dans la base de données
                flash('Erreur lors de la création du compte élève', 'danger')

        # Récupérer la liste des élèves depuis la base de données pour le menu déroulant
        with db.cursor() as cursor:
            cursor.execute('SELECT IdEleve, Nom, Prenom FROM eleve')
            eleves = cursor.fetchall()

        # Rediriger vers la même page pour afficher les messages flash
        return render_template('admin/create/create-compte-eleve.html', eleves=eleves)
    else:
        # Récupérer la liste des élèves depuis la base de données pour le menu déroulant
        with db.cursor() as cursor:
            cursor.execute('SELECT IdEleve, Nom, Prenom FROM eleve')
            eleves = cursor.fetchall()

        return render_template('admin/create/create-compte-eleve.html', eleves=eleves)


@app.route('/read')
def read():
    with db.cursor() as cursor:
        cursor.execute('SELECT Pseudo, "formateur" as role FROM CompteFormateur UNION SELECT Pseudo, "eleve" as role FROM CompteEleve')
        users = cursor.fetchall()
    return render_template('admin/read.html', users=users)

@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        user_id = request.form.get('id')
        role = request.form.get('role')
        pseudo = request.form.get('pseudo')
        mot_de_passe = request.form.get('password')

        table = 'CompteFormateur' if role == 'formateur' else 'CompteEleve'
        update_fields = []
        update_values = []

        if pseudo:
            update_fields.append('Pseudo=%s')
            update_values.append(pseudo)
        if mot_de_passe:
            hashed_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
            update_fields.append('MotDePasse=%s')
            update_values.append(hashed_password)

        update_values.append(user_id)

        with db.cursor() as cursor:
            cursor.execute(f'UPDATE {table} SET {", ".join(update_fields)} WHERE IdFormateur=%s' if role == 'formateur' else f'UPDATE {table} SET {", ".join(update_fields)} WHERE IdCompteEleve=%s', update_values)
            db.commit()

        return jsonify({'message': 'Utilisateur mis à jour avec succès'})
    return render_template('admin/update.html')

from flask import jsonify

@app.route('/delete_eleve', methods=['POST', 'GET'])
def delete_eleve():
    if request.method == 'POST':
        eleve_id = request.form.get('eleve_id')

        # Supprimer l'élève de la base de données
        with db.cursor() as cursor:
            cursor.execute('DELETE FROM Eleve WHERE IdEleve=%s', (eleve_id,))
            db.commit()

        flash('Élève supprimé avec succès', 'success')
        return redirect(url_for('delete_eleve'))

    # Récupérer les élèves pour l'affichage dans le menu déroulant
    with db.cursor() as cursor:
        cursor.execute('SELECT IdEleve AS Id, Nom, Prenom FROM Eleve')
        eleves = cursor.fetchall()

    return render_template('admin/delete/delete_eleve.html', eleves=eleves)

@app.route('/delete_formateur', methods=['POST', 'GET'])
def delete_formateur():
    if request.method == 'POST':
        formateur_id = request.form.get('formateur_id')

        # Supprimer le formateur de la base de données
        with db.cursor() as cursor:
            cursor.execute('DELETE FROM Formateur WHERE IdFormateur=%s', (formateur_id,))
            db.commit()

        flash('Formateur supprimé avec succès', 'success')
        return redirect(url_for('delete_formateur'))

    # Récupérer les formateurs pour l'affichage dans le menu déroulant
    with db.cursor() as cursor:
        cursor.execute('SELECT IdFormateur AS Id, Nom, Prenom FROM Formateur')
        formateurs = cursor.fetchall()

    return render_template('admin/delete/delete_formateur.html', formateurs=formateurs)



@app.route('/ajouter-eleve', methods=['POST'])
def ajouter_eleve():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']
        classe_id = request.form['classe']

        # Insérer les données de l'élève dans la base de données
        with db.cursor() as cursor:
            try:
                cursor.execute('INSERT INTO Eleve (Nom, Prenom, Email, Telephone, IDClasse) VALUES (%s, %s, %s, %s, %s)', (nom, prenom, email, telephone, classe_id))
                db.commit()
                flash('Élève ajouté avec succès!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Une erreur s\'est produite: {str(e)}', 'danger')

        # Rediriger vers la même page avec le message flash
        return redirect(url_for('create_eleve'))
    else:
        # Gérer les autres méthodes HTTP
        return 'Méthode non autorisée', 405
    
@app.route('/ajouter-formateur', methods=['POST'])
def ajouter_formateur():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']

        # Insérer les données du formateur dans la base de données
        with db.cursor() as cursor:
            try:
                cursor.execute('INSERT INTO formateur (Nom, Prenom, Email, Telephone) VALUES (%s, %s, %s, %s)', (nom, prenom, email, telephone))
                db.commit()
                flash('Formateur ajouté avec succès', 'success')
            except Exception as e:
                flash('Une erreur est survenue lors de l\'ajout du formateur', 'error')
                db.rollback()

        # Rediriger vers la même page
        return redirect(url_for('create_formateur'))
    else:
        # Gérer les autres méthodes HTTP
        return 'Méthode non autorisée', 405
    




@app.route('/update/eleve', methods=['GET', 'POST'])
def update_eleve():
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute('SELECT * FROM eleve')
        eleves = cursor.fetchall()
        cursor.execute('SELECT * FROM classe')
        classes = cursor.fetchall()
        return render_template('admin/update/update_eleve.html', eleves=eleves, classes=classes)
    elif request.method == 'POST':
        eleve_id = request.form['eleve_id']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM eleve WHERE IdEleve = %s', (eleve_id,))
        eleve = cursor.fetchone()
        cursor.execute('SELECT * FROM classe')
        classes = cursor.fetchall()
        if eleve:
            
            return render_template('admin/update/update_eleve_form.html', eleve=eleve, classes=classes)
        else:
            flash('Élève introuvable.', 'danger')
            return redirect(url_for('update_eleve'))

from flask import redirect, url_for, request, flash

@app.route('/update/eleve/update', methods=['POST'])
def update_eleve_post():
    eleve_id = request.form['eleve_id']
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    id_classe = request.form['id_classe']
    
    cursor = db.cursor()
    cursor.execute('UPDATE eleve SET Nom=%s, Prenom=%s, Email=%s, Telephone=%s, IDClasse=%s WHERE IdEleve=%s',
                   (nom, prenom, email, telephone, id_classe, eleve_id))
    db.commit()
    
    flash('Les informations de l\'élève ont été mises à jour avec succès.', 'success')
    return redirect(url_for('update_eleve'))



@app.route('/update/formateur', methods=['GET', 'POST'])
def update_formateur():
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute('SELECT * FROM formateur')
        formateurs = cursor.fetchall()
        return render_template('admin/update/update_formateur.html', formateurs=formateurs)
    elif request.method == 'POST':
        formateur_id = request.form['formateur_id']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM formateur WHERE IdFormateur = %s', (formateur_id,))
        formateur = cursor.fetchone()
        if formateur:
            return render_template('admin/update/update_formateur_form.html', formateur=formateur)
        else:
            flash('Formateur introuvable.', 'danger')
            return redirect(url_for('update_formateur'))

@app.route('/update/formateur/update', methods=['POST'])
def update_formateur_post():
    formateur_id = request.form['formateur_id']
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    
    cursor = db.cursor()
    cursor.execute('UPDATE formateur SET Nom=%s, Prenom=%s, Email=%s, Telephone=%s WHERE IdFormateur=%s',
                   (nom, prenom, email, telephone, formateur_id))
    db.commit()
    
    flash('Les informations du formateur ont été mises à jour avec succès.', 'success')
    return redirect(url_for('update_formateur'))



@app.route('/update/compte_eleve', methods=['GET', 'POST'])
def update_compte_eleve():
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute('SELECT * FROM compteeleve')
        comptes = cursor.fetchall()
        return render_template('admin/update/update_compte_eleve.html', comptes=comptes)
    elif request.method == 'POST':
        compte_id = request.form['compte_id']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM compteeleve WHERE IdCompteEleve = %s', (compte_id,))
        compte = cursor.fetchone()
        if compte:
            return render_template('admin/update/update_compte_eleve_form.html', compte=compte)
        else:
            flash('Compte élève introuvable.', 'danger')
            return redirect(url_for('update_compte_eleve'))

@app.route('/update/compte_eleve/update', methods=['POST'])
def update_compte_eleve_post():
    compte_id = request.form['compte_id']
    pseudo = request.form['pseudo']
    mot_de_passe = request.form['mot_de_passe']
    
    cursor = db.cursor()
    cursor.execute('UPDATE compteeleve SET Pseudo=%s, MotDePasse=%s WHERE IdCompteEleve=%s',
                   (pseudo, mot_de_passe, compte_id))
    db.commit()
    
    flash('Les informations du compte élève ont été mises à jour avec succès.', 'success')
    return redirect(url_for('update_compte_eleve'))



@app.route('/update/compte_formateur', methods=['GET', 'POST'])
def update_compte_formateur():
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute('SELECT * FROM compteformateur')
        comptes = cursor.fetchall()
        return render_template('admin/update/update_compte_formateur.html', comptes=comptes)
    elif request.method == 'POST':
        compte_id = request.form['compte_id']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM compteformateur WHERE IDCompteFormateur = %s', (compte_id,))
        compte_formateur = cursor.fetchone()
        if compte_formateur:
            return render_template('admin/update/update_compte_formateur_form.html', compte_formateur=compte_formateur)
        else:
            flash('Compte formateur introuvable.', 'danger')
            return redirect(url_for('update_compte_formateur'))

@app.route('/update/compte_formateur/update', methods=['POST'])
def update_compte_formateur_post():
    compte_id = request.form['compte_id']
    pseudo = request.form['pseudo']
    mot_de_passe = request.form['mot_de_passe']
    
    cursor = db.cursor()
    cursor.execute('UPDATE compteformateur SET Pseudo=%s, MotDePasse=%s WHERE IDCompteFormateur=%s',
                   (pseudo, mot_de_passe, compte_id))
    db.commit()
    
    flash('Les informations du compte formateur ont été mises à jour avec succès.', 'success')
    return redirect(url_for('update_compte_formateur'))
