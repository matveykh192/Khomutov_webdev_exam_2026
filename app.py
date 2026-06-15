import os
from flask import Flask
from flask import render_template
from routes.books import books_bp

from flask_login import LoginManager

from config import Config

from routes.statistics import statistics_bp

from models import (
    db,
    User
)

from routes.auth import auth_bp


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)

app.config.from_object(
    Config
)

db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "auth.login"

login_manager.login_message = (
    "Для выполнения данного действия необходимо пройти процедуру аутентификации"
)

app.register_blueprint(
    auth_bp
)

app.register_blueprint(books_bp)


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

app.register_blueprint(
    statistics_bp
)

if __name__ == "__main__":
    app.run(
        debug=True
    )