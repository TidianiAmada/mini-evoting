from datetime import datetime
from app import db

class Election(db.Model):
    id_election = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    date_heure_debut = db.Column(db.DateTime, nullable=False)
    date_heure_fin = db.Column(db.DateTime, nullable=False)
    candidats = db.relationship('Candidat', backref='election', lazy=True)
    organisateur = db.relationship('Organisateur', backref='election', uselist=False)
    modalites = db.Column(db.Text, nullable=True)

class Organisateur(db.Model):
    cni = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(60), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id_election'), nullable=True)

class Electeur(db.Model):
    cne = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)

class Candidat(db.Model):
    id_cnd = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(150), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id_election'), nullable=False)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cne = db.Column(db.String(20), db.ForeignKey('electeur.cne'), nullable=False)
    id_cnd_premier_choix = db.Column(db.Integer, db.ForeignKey('candidat.id_cnd'), nullable=False)
    id_cnd_second_choix = db.Column(db.Integer, db.ForeignKey('candidat.id_cnd'), nullable=True)
    date_de_vote = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Voix(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_election = db.Column(db.Integer, db.ForeignKey('election.id_election'), nullable=False)
    id_cnd = db.Column(db.Integer, db.ForeignKey('candidat.id_cnd'), nullable=False)
    total_voix = db.Column(db.Integer, nullable=False)
    pourcentage = db.Column(db.Float, nullable=False)
    rang = db.Column(db.Integer, nullable=False)

class Resultat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre_election = db.Column(db.String(150), nullable=False)
    list_des_voix = db.Column(db.Text, nullable=False)
