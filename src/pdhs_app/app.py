import os
from flask import Flask
from database.db import db, migrate
from middleware.security import jwt
from flask_cors import CORS

# import Blueprints
from middleware.auth import bp as auth_bp
from pdhs_app.blueprints.user_routes import bp as user_bp
from pdhs_app.blueprints.document_routes import bp as document_bp
from pdhs_app.blueprints.department_routes import bp as department_bp
from pdhs_app.blueprints.college_routes import bp as college_bp
from pdhs_app.blueprints.faculty_routes import bp as faculty_bp
from pdhs_app.blueprints.comment_routes import bp as comment_bp
from pdhs_app.blueprints.portfolio_routes import bp as portfolio_bp
from pdhs_app.blueprints.approval_routes import bp as approval_bp


def create_app(*args, **kwargs):
    """
    Initialize core application using app factory.
    """
    try:
        env = kwargs['env']
    except KeyError as e:
        env = 'development'
        print('Error:', e, 'Environment was not specified, defaulting to development')

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config['ENV'] = env
    app.config.from_object('config.%s' % env)

    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize CORS
    CORS(app)

    # Initialize JWT
    jwt.init_app(app)

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    @app.route('/')
    def hello():
        return "Hello from root of app /"

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(document_bp, url_prefix="/documents")
    app.register_blueprint(department_bp, url_prefix="/deparments")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(college_bp, url_prefix="/colleges")
    app.register_blueprint(faculty_bp, url_prefix="/faculties")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolios")
    app.register_blueprint(approval_bp, url_prefix="/approvals")

    with app.app_context():
        # Reset Database
        db.drop_all()   # Comment out if you want to use flask_migrate
        db.create_all()  # Comment out if you want to use flask_migrate
    return app
