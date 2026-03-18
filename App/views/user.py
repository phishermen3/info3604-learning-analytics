from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies
from .log import log_views
from .auth import auth_views
from App.models import User
from App.controllers import (
    change_user_password,
    jwt_required
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/account', methods=['GET'])
@jwt_required()
def account_page():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        flash("User session expired. Please log in again.")
        return redirect(url_for('auth_views.login'))
    
    return render_template('account.html', current_user=user)

@user_views.route('/account/change-password', methods=['POST'])
@jwt_required(locations=["cookies"])
def change_password_action():
    data = request.form
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        flash("User session expired. Please log in again.")
        return redirect(url_for('auth_views.login'))
        
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm = data.get('confirm_password')
    
    if not user.check_password(current_password):
        return jsonify({"success": False, "message": "Current Password is Incorrect"}), 400
    
    if not new_password or len(new_password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters long"}), 400
    
    if new_password != confirm:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    success, error = change_user_password(user, new_password)
    
    if success:
        flash("Password updated!")
        new_access_token = create_access_token(identity=identity, additional_claims={"force_password_change": False})
        new_refresh_token = create_refresh_token(identity=identity, additional_claims={"force_password_change": False})
        response = jsonify({"success": True})
        set_access_cookies(response, new_access_token)
        set_refresh_cookies(response, new_access_token)
        return response
    else:
        return jsonify({"success": False, "message": error}), 500
