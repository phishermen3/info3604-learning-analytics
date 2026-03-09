from flask import Blueprint
from flask import render_template
from flask import jsonify
from types import SimpleNamespace

TeamMembership_bp = Blueprint("TeamMembership", __name__)

@TeamMembership_bp.route("/courses/<int:course_id>/membership", methods=["GET"])
def check_membership(course_id: int):
 
    current_user = getattr(check_membership, "current_user", SimpleNamespace(is_authenticated=False, id=None))
    session = getattr(check_membership, "session", None)
    
    try:
        if not current_user or not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        memberships = getattr(session, "memberships", [])

        already_member = any(
            m.user_id == current_user.id and
            m.course_id == course_id
            for m in memberships
        )

        if already_member:
            return jsonify({
                "error": "User already belongs to a team in this course"
            }), 409

        enrolled = getattr(session, "enrolled", False)
        return jsonify({"enrolled": enrolled}), 200
    finally:
        if session and hasattr(session, "close"):
            session.close()