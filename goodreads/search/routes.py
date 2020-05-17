from flask import (render_template, g, Blueprint, redirect, url_for)
from goodreads.models import Book


search_engine = Blueprint('search_engine', __name__)


@search_engine.route('/search_results/<string:query>')
def search_results(query):
    results = Book.query.filter(Book.title.contains(query)).all()
    return render_template('search_results.html', query=query, results=results)


@search_engine.route('/search', methods=["POST"])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('main.home'))
    return redirect(url_for('search_engine.search_results', query=g.search_form.name.data))
