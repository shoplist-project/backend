from flask import Flask
from config import Config
from models import db
from routes import api
from flask_migrate import Migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=not Config.PRODUCTION)
