import os
from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from flask_jwt_extended import jwt_required, current_user
from App.controllers import create_user, initialize
from dotenv import load_dotenv

load_dotenv()

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/app', methods=['GET'])
@jwt_required()
def home():
    return render_template('index.html')

@index_views.route('/init', methods=['GET'])
def init():
    if os.getenv("ENV") == "PRODUCTION":
        return "Action forbidden in production", 403
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})