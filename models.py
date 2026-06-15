from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


book_genres = db.Table(
    "book_genres",

    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    ),

    db.Column(
        "genre_id",
        db.Integer,
        db.ForeignKey(
            "genres.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    users = db.relationship(
        "User",
        back_populates="role"
    )


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    login = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    last_name = db.Column(
        db.String(100),
        nullable=False
    )

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    middle_name = db.Column(
        db.String(100)
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False
    )

    role = db.relationship(
        "Role",
        back_populates="users"
    )

    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    views = db.relationship(
        "BookView",
        back_populates="user"
    )

    def has_role(self, role_name):
        return (
            self.role
            and self.role.name.lower() == role_name.lower()
        )

    @property
    def full_name(self):

        result = (
            f"{self.last_name} "
            f"{self.first_name}"
        )

        if self.middle_name:
            result += f" {self.middle_name}"

        return result

class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    books = db.relationship(
        "Book",
        secondary=book_genres,
        back_populates="genres"
    )


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=False
    )

    publisher = db.Column(
        db.String(255),
        nullable=False
    )

    author = db.Column(
        db.String(255),
        nullable=False
    )

    pages = db.Column(
        db.Integer,
        nullable=False
    )

    genres = db.relationship(
        "Genre",
        secondary=book_genres,
        back_populates="books"
    )

    cover = db.relationship(
        "Cover",
        uselist=False,
        back_populates="book",
        cascade="all, delete-orphan"
    )

    reviews = db.relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    views = db.relationship(
        "BookView",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    @property
    def average_rating(self):

        if not self.reviews:
            return 0

        return round(
            sum(r.rating for r in self.reviews)
            / len(self.reviews),
            2
        )

    @property
    def reviews_count(self):
        return len(self.reviews)

class Cover(db.Model):
    __tablename__ = "covers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    file_name = db.Column(
        db.String(255),
        nullable=False
    )

    mime_type = db.Column(
        db.String(100),
        nullable=False
    )

    md5_hash = db.Column(
    db.String(32),
    nullable=False,
    unique=True
)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    book = db.relationship(
        "Book",
        back_populates="cover"
    )

class Review(db.Model):
    __tablename__ = "reviews"

    __table_args__ = (
    db.UniqueConstraint(
        "book_id",
        "user_id",
        name="uq_review_user_book"
    ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    book = db.relationship(
        "Book",
        back_populates="reviews"
    )

    user = db.relationship(
        "User",
        back_populates="reviews"
    )

class BookView(db.Model):
    __tablename__ = "book_views"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE")
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id", ondelete="CASCADE")
    )

    viewed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="views"
    )

    book = db.relationship(
        "Book",
        back_populates="views"
    )

class VisitLog(db.Model):
    __tablename__ = "visit_log"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        )
    )

    viewed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    book = db.relationship(
        "Book"
    )

    user = db.relationship(
        "User"
    )