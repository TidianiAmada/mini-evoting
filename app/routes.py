from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import db, Election, Candidat, Electeur, Vote, Voix, Organisateur
from .services import calculate_results, count_vote
from datetime import datetime

from werkzeug.security import check_password_hash  # Assuming passwords are hashed
main = Blueprint('main', __name__)


# Login for Organisateurs and Electeurs
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form['user_type']  # Organisateur or Electeur
        email_or_cne = request.form['email_or_cne']
        password = request.form['password']

        if user_type == 'organisateur':
            # Login as Organisateur
            user = Organisateur.query.filter_by(email=email_or_cne).first()
            if user and check_password_hash(user.mot_de_passe, password):
                session['user_id'] = user.cni  # Store CNI in session
                session['role'] = 'organisateur'
                return redirect(url_for('main.create_election'))
            else:
                flash('Invalid credentials for Organisateur')

        elif user_type == 'electeur':
            # Login as Electeur
            user = Electeur.query.filter_by(cne=email_or_cne).first()
            if user:
                session['user_id'] = user.cne  # Store CNE in session
                session['role'] = 'electeur'
                return redirect(url_for('main.vote'))
            else:
                flash('Invalid credentials for Electeur')

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
    return render_template('register_electeur.html')

# Voting route
@main.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        cne = request.form['cne']
        id_cnd_premier_choix = request.form['id_cnd_premier_choix']
        id_cnd_second_choix = request.form['id_cnd_second_choix']
        date_de_vote = datetime.now()
        
        # Save the vote to the Vote table
        vote = Vote(cne=cne, id_cnd_premier_choix=id_cnd_premier_choix, 
                    id_cnd_second_choix=id_cnd_second_choix, date_de_vote=date_de_vote)
        db.session.add(vote)
        db.session.commit()
        
        return redirect(url_for('main.results'))
    
    candidats = Candidat.query.all()  # Get all candidates for display
    return render_template('vote.html', candidats=candidats)

# Step 5: Displaying Results

@main.route('/results/<int:election_id>', methods=['GET'])
def results(election_id):
    results = count_vote(election_id)
    return render_template('results.html', results=results)


