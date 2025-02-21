from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = "your_super_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'library.sqlite')  #

db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
        Home page that displays all books in the library.

        - GET: Retrieves all books from the database
        - POST: Handles book deletion requests (if a book is deleted, it also removes the author if no books remain).
        - Sorting: Supports sorting books by title or author in ascending or descending order.
        - Searching: Allows filtering

        Returns:
            Rendered template of home.html with books data.
        """
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'title')
    direction = request.args.get('direction', 'asc')

    books_query = Book.query.join(Author)

    if search_query:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Author.name.ilike(f"%{search_query}%"))
        )

    if sort_by == "author":
        books_query = books_query.order_by(
            Author.name.asc() if direction == "asc" else Author.name.desc()
        )
    else:
        books_query = books_query.order_by(
            Book.title.asc() if direction == "asc" else Book.title.desc()
        )

    books = books_query.all()

    if request.method == 'POST':
        book_id_to_delete = request.form.get('delete_book_id')

        if book_id_to_delete:
            try:
                book_id_to_delete = int(book_id_to_delete)  # Sicherstellen, dass es eine gültige ID ist
                book_to_delete = Book.query.get(book_id_to_delete)

                if book_to_delete:
                    author_id = book_to_delete.author_id  # Autor speichern
                    db.session.delete(book_to_delete)
                    db.session.commit()

                    # Falls der Autor keine weiteren Bücher mehr hat -> Autor löschen
                    remaining_books = Book.query.filter_by(author_id=author_id).count()
                    if remaining_books == 0:
                        author_to_delete = Author.query.get(author_id)
                        if author_to_delete:
                            db.session.delete(author_to_delete)
                            db.session.commit()

                    flash("Book successfully deleted!", "success")
                else:
                    flash("Book ID not found!", "error")

            except ValueError:  # Falls die Eingabe keine Zahl ist
                flash("Invalid book ID!", "error")

        return redirect(url_for('home'))  # Seite neu laden, um die gelöschten Bücher nicht mehr anzuzeigen

    return render_template('home.html', books=books, search_query=search_query)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
        Adding a new author to the library.

        - GET: Displays the add_author.html form.
        - POST: Processes form data, validates input, and adds a new author to the database.
          - If required fields are missing, flashes an error message.
          - If successful, flashes a confirmation message and redirects back.

        Returns:
            Rendered template of add_author.html with a success/error message.
        """
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birthdate')
        date_of_death = request.form.get('date_of_death')

        if not name or not birth_date:
            flash("Please insert all required dates.")

        else:
            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()
            flash("Author successfully added!")

        flash("Author successfully added!", "success")
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
        Adding a new book to the library.

        - GET: Displays the add_book.html form with a dropdown to select an existing author.
        - POST: Processes form data, validates input, and adds a new book to the database.
          - If required fields are missing, flashes an error message.
          - If successful, flashes a confirmation message and redirects back.

        Returns:
            Rendered template of add_book.html with a success/error message.
        """
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not isbn or not title or not publication_year or not author_id:
            flash("Please fill in all fields.")
        else:
            new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(new_book)
            db.session.commit()
            flash("Book successfully added!")

        return redirect(url_for('add_book'))

    return render_template('add_book.html', authors=authors)


@app.route("/clear_flash", methods=["POST"])
def clear_flash():
    session.pop('_flashes', None)  # Clear Flash-message
    return '', 204


@app.route('/library')
def library_home():
    sort_by = request.args.get('sort_by', 'title')
    direction = request.args.get('direction', 'asc')

    if sort_by not in ['title', 'author']:
        sort_by = 'title'

    order = Book.title if sort_by == 'title' else Author.name
    if direction == 'desc':
        order = order.desc()

    books = Book.query.join(Author).order_by(order).all()
    return render_template('home.html', books=books)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
        Deletes a book from the library.

        - Finds the book by its ID.
        - If found, deletes the book and removes the author if they have no remaining books.
        - If the book does not exist, flashes an error message.
        - Redirects back to the home page after deletion.

        Returns:
            Redirect to home.html with a success/error message.
        """
    book = Book.query.get(book_id)

    if book:
        author = book.author
        db, session.delete(book)
        db.session.commit

        remaining_books = Book.query.filter_by(author_id=author.id).count()
        if remaining_books == 0:
            db.session.delete(author)
            db.session.commit()

        flash("Book deleted!", "success")
    else:
        flash("Book not found.", "danger")

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)

# with app.app_context():
# db.create_all()
