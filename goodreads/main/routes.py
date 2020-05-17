from flask import render_template, Blueprint
from goodreads.utils import get_updates
from goodreads.models import User

main = Blueprint('main', __name__)


@main.route('/')
def home():
    users = User.query.all()
    return render_template('home.html', updates=get_updates(users))
