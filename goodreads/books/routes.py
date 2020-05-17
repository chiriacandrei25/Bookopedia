from flask_login import login_required, current_user
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from goodreads.books.forms import BookForm
from goodreads.models import Book, Shelf, BookInShelf
from goodreads import db
from goodreads.utils import save_picture
from goodreads.users.utils import user_recommended_books


books = Blueprint('books', __name__)


@books.route("/books/new", methods=['GET', 'POST'])
@login_required
def create_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, description=form.description.data, author=current_user)
        if form.picture.data:
            book.image_file = save_picture(form.picture.data, 'static/pics/book_covers')
        db.session.add(book)
        db.session.commit()
        flash('Your book has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_book.html', form=form, legend='New book')


@books.route("/books/<int:book_id>")
def book(book_id):
    book = Book.query.get_or_404(book_id)
    review = next((review for review in book.reviews if review.user == current_user), None)
    return render_template('book.html', book=book, my_review=review)


@books.route("/books/<int:book_id>/update", methods=['POST', 'GET'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.author != current_user:
        abort(403)
    form = BookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.description = form.description.data
        db.session.commit()
        flash('Your book has been updated!', 'success')
        return redirect(url_for('books.book', book_id=book_id))
    if request.method == 'GET':
        form.title.data = book.title
        form.description.data = book.description
    return render_template('update_book.html', form=form)


@books.route("/books/<int:book_id>/delete", methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.author != current_user:
        abort(403)
    for review in book.reviews:
        db.session.delete(review)
    db.session.delete(book)
    db.session.commit()
    flash('Your book has been removed!', 'success')
    return redirect(url_for('main.home'))


@books.route("/books/<int:book_id>/add/<int:shelf_id>", methods=['POST'])
@login_required
def add_to_shelf(book_id, shelf_id):
    book = Book.query.get_or_404(book_id)
    shelf = Shelf.query.get_or_404(shelf_id)
    if shelf.owner != current_user:
        abort(403)
    if book in [bookInShelf.book for bookInShelf in shelf.books]:
        flash('The book is already in this shelf', 'danger')
    else:
        bookInShelf = BookInShelf(book=book)
        shelf.books.append(bookInShelf)
        db.session.commit()
        flash('The book has been added to your shelf!', 'success')
    review = next((review for review in book.reviews if review.user == current_user), None)
    return render_template('book.html', book=book, my_review=review)


@books.route("/books/all_books", methods=['GET'])
@login_required
def all_books():
    books = Book.query.all()
    return render_template('all_books.html', books=books)


@books.route("/books/recommend_books", methods=['GET'])
@login_required
def recommend_books():
    books = user_recommended_books(current_user)
    return render_template('all_books.html', books=books)
