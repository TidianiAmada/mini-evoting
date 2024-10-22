from .models import Vote, Voix, Candidat, db
from sqlalchemy import func


def calculate_results(election_id):
    # Step 1: Get first-choice votes for each candidate
    first_choice_votes = db.session.query(Vote.id_cnd_premier_choix, func.count(Vote.id).label('vote_count'))\
        .filter(Vote.election_id == election_id)\
        .group_by(Vote.id_cnd_premier_choix).all()

    # Step 2: Store results in a dictionary for easy access
    candidate_votes = {candidate_id: vote_count for candidate_id, vote_count in first_choice_votes}

    # Step 3: Check if there's a clear winner (majority)
    total_votes = sum(candidate_votes.values())
    majority = total_votes / 2

    for candidate_id, vote_count in candidate_votes.items():
        if vote_count > majority:
            return save_results(election_id, candidate_votes)  # Clear winner, return results

    # Step 4: If no clear majority, redistribute votes
    while len(candidate_votes) > 1:
        # Find the candidate with the fewest votes
        candidate_with_least_votes = min(candidate_votes, key=candidate_votes.get)
        
        # Remove this candidate and redistribute their votes
        second_choice_votes = db.session.query(Vote.id_cnd_second_choix, func.count(Vote.id).label('vote_count'))\
            .filter(Vote.id_cnd_premier_choix == candidate_with_least_votes)\
            .group_by(Vote.id_cnd_second_choix).all()

        # Redistribute votes to remaining candidates
        for second_choice_candidate_id, vote_count in second_choice_votes:
            if second_choice_candidate_id in candidate_votes:
                candidate_votes[second_choice_candidate_id] += vote_count

        # Remove the eliminated candidate from the dictionary
        del candidate_votes[candidate_with_least_votes]

        # Check if a candidate has achieved a majority
        for candidate_id, vote_count in candidate_votes.items():
            if vote_count > majority:
                return save_results(election_id, candidate_votes)  # Found a winner, save results

    return save_results(election_id, candidate_votes)

def count_vote(election_id):
    # Étape 1 : Obtenir le nombre total de voix
    total_votes = db.session.query(func.count(Vote.id)).filter_by(election_id=election_id).scalar()

    # Étape 2 : Compter les voix de premier choix pour chaque candidat
    first_choice_votes = db.session.query(Vote.id_cnd_premier_choix, func.count(Vote.id).label('vote_count'))\
        .filter_by(election_id=election_id)\
        .group_by(Vote.id_cnd_premier_choix).all()

    # Étape 3 : Organiser les votes dans un dictionnaire
    candidate_votes = {candidate_id: vote_count for candidate_id, vote_count in first_choice_votes}

    # Étape 4 : Vérifier s'il y a une majorité absolue
    majority = total_votes / 2
    for candidate_id, vote_count in candidate_votes.items():
        if vote_count > majority:
            return save_results(election_id, candidate_votes)  # Gagnant trouvé, retourner les résultats

    # Étape 5 : Si pas de majorité, commencer à éliminer les candidats et redistribuer les votes
    while len(candidate_votes) > 1:
        # Trouver le candidat avec le moins de votes
        candidate_with_least_votes = min(candidate_votes, key=candidate_votes.get)
        
        # Obtenir les votes de deuxième choix pour ceux qui ont voté pour le candidat éliminé
        second_choice_votes = db.session.query(Vote.id_cnd_second_choix, func.count(Vote.id).label('vote_count'))\
            .filter(Vote.id_cnd_premier_choix == candidate_with_least_votes)\
            .group_by(Vote.id_cnd_second_choix).all()

        # Redistribuer les votes aux candidats restants
        for second_choice_candidate_id, vote_count in second_choice_votes:
            if second_choice_candidate_id in candidate_votes:
                candidate_votes[second_choice_candidate_id] += vote_count

        # Retirer le candidat éliminé de la course
        del candidate_votes[candidate_with_least_votes]

        # Vérifier à nouveau s'il y a une majorité
        for candidate_id, vote_count in candidate_votes.items():
            if vote_count > majority:
                return save_results(election_id, candidate_votes)  # Gagnant trouvé, sauvegarder les résultats

    # Si un seul candidat reste, il est le gagnant
    return save_results(election_id, candidate_votes)

def save_results(election_id, candidate_votes):
    # Effacer les résultats précédents s'il y en a
    Voix.query.filter_by(id_election=election_id).delete()

    # Sauvegarder les décomptes de voix finaux et les pourcentages pour chaque candidat
    total_votes = sum(candidate_votes.values())  # Calculer le total ici pour éviter de le recalculer plusieurs fois

    results = []
    for candidate_id, vote_count in candidate_votes.items():
        pourcentage = (vote_count / total_votes) * 100
        rang = sorted(candidate_votes.values(), reverse=True).index(vote_count) + 1

        voix = Voix(
            id_election=election_id,
            id_cnd=candidate_id,
            total_voix=vote_count,
            pourcentage=pourcentage,
            rang=rang
        )
        db.session.add(voix)
        results.append({'id': candidate_id, 'votes': vote_count, 'pourcentage': pourcentage, 'rang': rang})

    db.session.commit()

    # Retourner le résultat final pour chaque candidat, y compris le nom et le prénom
    return db.session.query(Voix, Candidat)\
        .join(Candidat, Voix.id_cnd == Candidat.id_cnd)\
        .filter(Voix.id_election == election_id)\
        .all()
