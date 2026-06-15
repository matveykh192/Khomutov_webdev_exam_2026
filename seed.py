from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

DATABASE_URL = (
    "mysql+pymysql://root:qwerty123@127.0.0.1:3306/electronic_library"
)

engine = create_engine(DATABASE_URL)

roles = [
    (
        "administrator",
        "Полный доступ к системе"
    ),
    (
        "moderator",
        "Редактирование книг"
    ),
    (
        "user",
        "Оставление рецензий"
    )
]

genres = [
    "Фантастика",
    "Роман",
    "Детектив",
    "Ужасы",
    "Фэнтези",
    "Биография",
    "Научная литература",
    "История"
]


def seed_roles(connection):
    for name, description in roles:
        connection.execute(
            text("""
                INSERT INTO roles(name, description)
                VALUES(:name, :description)
            """),
            {
                "name": name,
                "description": description
            }
        )


def seed_genres(connection):
    for genre in genres:
        connection.execute(
            text("""
                INSERT INTO genres(name)
                VALUES(:name)
            """),
            {
                "name": genre
            }
        )


def seed_users(connection):

    users = [
        (
            "admin",
            "admin123",
            "Администратор",
            "Главный",
            "",
            1
        ),
        (
            "moderator",
            "mod123",
            "Модератор",
            "Главный",
            "",
            2
        ),
        (
            "user",
            "user123",
            "Пользователь",
            "Тестовый",
            "",
            3
        )
    ]

    for user in users:
        connection.execute(
            text("""
                INSERT INTO users(
                    login,
                    password_hash,
                    last_name,
                    first_name,
                    middle_name,
                    role_id
                )
                VALUES(
                    :login,
                    :password_hash,
                    :last_name,
                    :first_name,
                    :middle_name,
                    :role_id
                )
            """),
            {
                "login": user[0],
                "password_hash":
                    generate_password_hash(user[1]),
                "last_name": user[2],
                "first_name": user[3],
                "middle_name": user[4],
                "role_id": user[5]
            }
        )


with engine.begin() as connection:
    seed_roles(connection)
    seed_genres(connection)
    seed_users(connection)

print("База успешно заполнена.")