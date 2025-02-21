from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(10))
    date_of_death = db.Column(db.String(10), nullable=True)

    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name})>"

    def __str__(self):
        return f"{self.name} ({self.birth_date} - {self.date_of_death})"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author_id={self.author_id})>"

    def __str__(self):
        return f"'{self.title}' ({self.publication_year}) by {self.author.name}"
