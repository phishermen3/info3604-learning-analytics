import os
from flask import Flask, render_template, redirect, url_for, request
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import App
from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import all_views, setup_admin



def add_views(app):
    for view in all_views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    @app.before_request
    def password_check():
        allowed_routes = ['user_views.change_password_action', 'user_views.account_page', 'about_views.about', 'static', 'auth_views.login']
        if request.endpoint in allowed_routes:
            return
        try:
            verify_jwt_in_request()
        except Exception:
            return
        claims = get_jwt()
        if claims.get("force_password_change"):
            return redirect(url_for('user_views.account_page'))
    @jwt.expired_token_loader
    def handle_auth_error(jwt_header, jwt_payload):
        if jwt_payload['type'] == 'access':
            return redirect(url_for('auth_views.refresh_token_route'))
        else:
            return render_template('401.html', error="Session expired"), 401
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()
    return app