from flask import Flask, g
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from goodreads.search.forms import SearchForm
import numpy


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goodreads.db'
app.config['SECRET_KEY'] = 'ac2190ea983252ad1822c360406c37c3'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chiriac.andrei.alex@gmail.com'
app.config['MAIL_PASSWORD'] = 'Mlcinfoarena12345'
app.config['WTF_CSRF_ENABLED'] = False
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins='*')


from goodreads.users.routes import users
from goodreads.posts.routes import posts
from goodreads.main.routes import main
from goodreads.errors.handlers import errors
from goodreads.books.routes import books
from goodreads.authors.routes import authors
from goodreads.reviews.routes import reviews
from goodreads.shelves.routes import shelves
from goodreads.friendships.routes import friendships
from goodreads.requests.routes import requests
from goodreads.messages.routes import messages
from goodreads.notifications.routes import notifications
from goodreads.search.routes import search_engine

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(errors)
app.register_blueprint(books)
app.register_blueprint(reviews)
app.register_blueprint(shelves)
app.register_blueprint(friendships)
app.register_blueprint(requests)
app.register_blueprint(search_engine)
app.register_blueprint(messages)
app.register_blueprint(authors)
app.register_blueprint(notifications)


def avg_book_rating(book):
    if len(book.reviews) == 0:
        return -1, -1
    avg_rating = numpy.mean([review.rating for review in book.reviews])
    return int(avg_rating), avg_rating - int(avg_rating)


def user_liked_review(user, review):
    return next((like for like in review.likes if like.user == user), None) is not None


def format_number_of(item_list, item):
    if len(item_list) == 0:
        return ""
    if len(item_list) == 1:
        return "1 " + item
    return str(len(item_list)) + ' ' + item + 's'


@app.before_request
def before_request():
    g.search_form = SearchForm()
    g.avg_book_rating = avg_book_rating
    g.user_liked_review = user_liked_review
    g.format_number_of = format_number_of
