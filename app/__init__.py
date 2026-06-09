import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

    from .routes.auth import auth_bp
    from .routes.patients import patients_bp
    from .routes.doctors import doctors_bp
    from .routes.appointments import appointments_bp
    from .routes.billing import billing_bp
    from .routes.emergency import emergency_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(emergency_bp)

    return app