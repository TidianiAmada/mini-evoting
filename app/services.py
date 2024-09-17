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
    # Step 1: Get the total number of votes
    total_votes = db.session.query(func.count(Vote.id)).filter_by(election_id=election_id).scalar()

    # Step 2: Count first-choice votes for each candidate
    first_choice_votes = db.session.query(Vote.id_cnd_premier_choix, func.count(Vote.id).label('vote_count'))\
        .filter_by(election_id=election_id)\
        .group_by(Vote.id_cnd_premier_choix).all()

    # Step 3: Organize votes into a dictionary
    candidate_votes = {candidate_id: vote_count for candidate_id, vote_count in first_choice_votes}

    # Step 4: Check if there's an absolute majority (more than half of the votes)
    majority = total_votes / 2
    for candidate_id, vote_count in candidate_votes.items():
        if vote_count > majority:
            return save_results(election_id, candidate_votes)  # Winner found, return results

    # Step 5: If no majority, start eliminating candidates and redistributing votes
    while len(candidate_votes) > 1:
        # Find the candidate with the fewest votes
        candidate_with_least_votes = min(candidate_votes, key=candidate_votes.get)
        
        # Get the second-choice votes for those who voted for the eliminated candidate
        second_choice_votes = db.session.query(Vote.id_cnd_second_choix, func.count(Vote.id).label('vote_count'))\
            .filter(Vote.id_cnd_premier_choix == candidate_with_least_votes)\
            .group_by(Vote.id_cnd_second_choix).all()

        # Redistribute votes to remaining candidates
        for second_choice_candidate_id, vote_count in second_choice_votes:
            if second_choice_candidate_id in candidate_votes:
                candidate_votes[second_choice_candidate_id] += vote_count

        # Remove the eliminated candidate from the race
        del candidate_votes[candidate_with_least_votes]

        # Check again for a majority
        for candidate_id, vote_count in candidate_votes.items():
            if vote_count > majority:
                return save_results(election_id, candidate_votes)  # Winner found, save results

    # If only one candidate remains, they are the winner
    return save_results(election_id, candidate_votes)

def save_results(election_id, candidate_votes):
    # Clear previous results if any
    Voix.query.filter_by(election_id=election_id).delete()

    # Save the final vote counts and percentages for each candidate
    for candidate_id, vote_count in candidate_votes.items():
        total_votes = sum(candidate_votes.values())
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

    db.session.commit()

    # Return the final result for each candidate
    return Voix.query.filter_by(election_id=election_id).all()
