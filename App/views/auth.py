from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import (
    jwt_required, 
    current_user, 
    unset_jwt_cookies, 
    create_access_token,
    set_access_cookies,
    set_refresh_cookies
)

from.index import index_views

from App.controllers import (
    login,
    signup
)

auth_views = Blueprint('auth_views', __name__, url_prefix='/auth', template_folder='../templates')


'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id}")

@auth_views.route('/signup', methods=['POST'])
def signup_action():    
    data = request.form
    access_token, refresh_token = signup(data['password'])
    response = redirect(request.referrer or url_for('index'))
    if not access_token:
        flash('Signup failed')
        return response
    flash('Signup successful')
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    remember = request.form.get('remember') == 'on'
    access_token, refresh_token = login(data['user_code'], data['password'], remember)
    response = redirect(request.referrer or url_for('index'))
    if not access_token:
        flash('Login failed')
        return response
    flash('Login successful')
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer or url_for('index')) 
    flash("Logged out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/signup', methods=['POST'])
def user_signup_api():
    data = request.json
    access_token, refresh_token = signup(data['password'])
    if not access_token:
        return jsonify({'error': 'Signup failed'}), 400
    response = jsonify({'message': 'Signup successful'})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 201

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    remember = bool(data.get('remember', False))
    access_token, refresh_token = login(data['user_code'], data['password'], remember)
    if not access_token:
        return jsonify({'error': 'Login failed'}), 401
    response = jsonify({'message': 'Login successful'}) 
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 201

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = current_user.id
    new_access_token = create_access_token(identity=str(user_id))
    response = jsonify({'message': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f" id : {current_user.id}"})

