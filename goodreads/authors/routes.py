from flask import (render_template, Blueprint)
from goodreads.models import Author


authors = Blueprint('authors', __name__)


@authors.route("/authors/<int:author_id>")
def author(author_id):
    author = Author.query.get_or_404(author_id)
    print(author)
    return render_template('author.html', author=author)
