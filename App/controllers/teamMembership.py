from App.models import TeamMembership

def check_membership(team_id, user_id):
    membership = TeamMembership.query.filter_by(
        user_id=user_id,
        team_id=team_id
    ).first()

    return membership is not None