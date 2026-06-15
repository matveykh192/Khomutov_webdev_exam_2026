import os


class Config:

    SECRET_KEY = "super-secret-key"

    SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://root:qwerty123@127.0.0.1:3306/electronic_library"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(
        os.path.dirname(__file__)
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )