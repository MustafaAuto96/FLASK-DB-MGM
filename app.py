from flask import Flask
from config import Config
from extensions import db
from flask_migrate import Migrate
from flask_login import LoginManager
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    import logging
    logging.basicConfig (level=logging.DEBUG)
    app.logger.setLevel (logging.DEBUG)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes import main_bp
    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)