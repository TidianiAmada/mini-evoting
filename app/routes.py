from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import db, Election, Candidat, Electeur, Vote, Voix, Organisateur
from .services import calculate_results, count_vote
from datetime import datetime
import csv
import os
from werkzeug.security import check_password_hash  # Assuming passwords are hashed
main = Blueprint('main', __name__)


# Login for Organisateurs and Electeurs
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']  # Organisateur or Electeur
        
        print(user_type)
        if user_type == 'organisateur':
            cni = request.form['cni']
            password = request.form['password']
            
            if not cni or not password:
                print('CNI and password are required')
                return redirect(url_for('main.login'))
            
            # Login as Organisateur
            user = Organisateur.query.filter_by(cni=cni).first()
            if user:
                session['user_id'] = user.cni  # Store CNI in session
                session['role'] = 'organisateur'
                return redirect(url_for('main.create_election'))
            else:
                flash('Invalid credentials for Organisateur')

        elif user_type == 'electeur':
            cne = request.form['cne']
            
            if not cne:
                flash('CNE is required for Electeur')
                return redirect(url_for('main.login'))

            # Get the path to the CSV file in the project root
            csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fichier_electoral.csv')

            # Login as Electeur
            cne_found = False
            with open(csv_file_path, newline='', encoding='ISO-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['cne'] == cne:
                        cne_found = True
                        session['user_id'] = row['cne']  # Store CNE in session
                        session['role'] = 'electeur'
                        elc=Electeur(cne=cne,nom=row['nom'],prenom=row['prenom'])
                        db.session.add(elc)
                        db.session.commit()
                        return redirect(url_for('main.vote', election_id=row['election_id']))

            if not cne_found:
                flash('Invalid credentials for Electeur')

    # Clear only organisateur-specific session data
    session.pop('user_id', None)  # Assuming 'user_id' holds the organiser's session info
    session.pop('role', None)  # Remove the 'role' session
    return render_template('login.html')






# Create an election
@main.route('/election/create', methods=['GET', 'POST'])
def create_election():
    if request.method == 'POST':
        titre = request.form['titre']
        date_heure_debut = request.form['date_debut']  # Updated to match the form field name
        date_heure_fin = request.form['date_fin']      # Updated to match the form field name
        modalites = request.form['modalites']
        organisateur_cni = request.form['organisateur_cni']  # Assuming CNI of Organisateur is provided
        
        # Fetch the Organisateur using the CNI
        organisateur = Organisateur.query.filter_by(cni=organisateur_cni).first()

        if not organisateur:
            flash('Organisateur not found')
            return redirect(url_for('main.create_election'))

        # Save to Election table
        election = Election(titre=titre, 
                            date_heure_debut=date_heure_debut, 
                            date_heure_fin=date_heure_fin, 
                            modalites=modalites)

        # Link the Organisateur to this election
        election.organisateur = organisateur

        db.session.add(election)
        db.session.commit()
        election = Election.query.filter_by(titre=titre).first()

        return redirect(url_for('main.create_candidate', election_id=election.id_election))
    
    return render_template('election_form.html')



# Create a candidate
@main.route('/candidat/create', methods=['GET', 'POST'])
def create_candidate():
    election_id = request.args.get('election_id')
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        profession = request.form['profession']
        photo = request.form['photo']
        
        # Save to Candidat table
        candidat = Candidat(nom=nom, prenom=prenom, profession=profession, 
                            photo=photo, election_id=election_id)
        db.session.add(candidat)
        db.session.commit()
        
        return redirect(url_for('main.create_candidate', election_id=election_id))
    return render_template('candidate_form.html', election_id=election_id)


# Register a voter
@main.route('/electeur/register', methods=['GET', 'POST'])
def register_electeur():
    if request.method == 'POST':
        cne = request.form['cne']
        nom = request.form['nom']
        prenom = request.form['prenom']
        
        # Save to Electeur table
        electeur = Electeur(cne=cne, nom=nom, prenom=prenom)
        db.session.add(electeur)
        db.session.commit()

        return redirect(url_for('main.vote'))
    return render_template('voter_form.html')

# Voting route
@main.route('/vote', methods=['GET', 'POST'])
def vote():
    election_id = request.args.get('election_id')
    if request.method == 'POST':
        cne = request.form['cne']
        id_cnd_premier_choix = request.form['premier_choix']
        id_cnd_second_choix = request.form['second_choix']
        date_de_vote = datetime.now()
        
        # Save the vote to the Vote table
        vote = Vote(cne=cne, date_de_vote=date_de_vote, election_id=election_id)
        cnd_premier_choix= Candidat.query.filter_by(id_cnd=id_cnd_premier_choix).first()
        cnd_second_choix=Candidat.query.filter_by(id_cnd=id_cnd_second_choix).first()
        
        vote.cnd_premier_choix=cnd_premier_choix
        vote.cnd_second_choix=cnd_second_choix
        db.session.add(vote)
        db.session.commit()
         # After vote is processed, clear the session
        session.clear()  # This will remove all data from the session

        # Optionally, you can flash a message to confirm the user has voted
        flash('Thank you for voting. You have been logged out.')
        
        return redirect(url_for('main.login'))
    
    candidats = Candidat.query.all()  # Get all candidates for display
    return render_template('vote_form.html', candidats=candidats)

# Step 5: Displaying Results

@main.route('/results/<int:election_id>', methods=['GET'])
def results(election_id):
    results = count_vote(election_id)
    
    return render_template('results.html', results=results)


