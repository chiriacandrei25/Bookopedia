from flask_login import login_required, current_user
from flask import (render_template, url_for, flash, jsonify,
                   redirect, request, abort, Blueprint)
from goodreads.shelves.forms import ShelfForm
from goodreads.models import Shelf, Book
from goodreads import db
from goodreads.utils import get_updates


shelves = Blueprint('shelves', __name__)


@shelves.route("/shelves/new")
@login_required
def create_shelf():
    name = request.args.get('name')
    form = ShelfForm(shelf_name=name)
    if form.validate():
        shelf = Shelf(name=name, owner=current_user)
        db.session.add(shelf)
        db.session.commit()
    return jsonify(bookshelves=render_template('bookshelves.html', user=current_user),
                   new_shelf=render_template('new_shelf.html', form=form))


@shelves.route("/shelves/<int:shelf_id>")
def shelf(shelf_id):
    shelf = Shelf.query.get_or_404(shelf_id)
    if shelf is None:
        abort(404)
    return render_template('shelf.html', shelf=shelf)


@shelves.route("/shelves/<int:shelf_id>/update", methods=['POST', 'GET'])
@login_required
def update_shelf(shelf_id):
    shelf = Shelf.query.get_or_404(shelf_id)
    if shelf.owner != current_user:
        abort(403)
    form = ShelfForm()
    if form.validate_on_submit():
        shelf.name = form.name.data
        db.session.commit()
        flash('Your shelf has been updated!', 'success')
        return redirect(url_for('shelves.shelf', shelf_id=shelf_id))
    if request.method == 'GET':
        form.name.data = shelf.name
    return render_template('update_shelf.html', form=form, shelf=shelf)


@shelves.route("/shelves/delete")
@login_required
def delete_shelf():
    shelf_id = request.args.get('shelf_id')
    shelf = Shelf.query.get_or_404(shelf_id)
    if shelf.owner != current_user:
        abort(403)
    db.session.delete(shelf)
    db.session.commit()
    return jsonify(bookshelves=render_template('bookshelves.html', user=current_user),
                   news_feed=render_template('news_feed.html', updates=get_updates([current_user])))


@shelves.route("/shelves/remove-book")
@login_required
def remove_book():
    shelf_id = request.args.get('shelf_id')
    shelf = Shelf.query.get_or_404(shelf_id)
    if shelf.owner != current_user:
        abort(403)
    book_id = request.args.get('book_id')
    book = Book.query.get_or_404(book_id)
    try:
        idx = [bookInShelf.book for bookInShelf in shelf.books].index(book)
        bookInShelf = shelf.books[idx]
        shelf.books.remove(bookInShelf)
        db.session.commit()
        return jsonify(result=render_template('books_in_shelf.html', shelf=shelf))
    except(ValueError):
        abort(403)
