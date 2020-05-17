import os
import secrets
from PIL import Image
from flask import current_app
from goodreads.models import Review, Shelf, UserLikedReview, UserCommentedReview


def save_picture(form_picture, folder_path):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, folder_path, picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def get_user_updates(user):
    reviews = Review.query.filter_by(user=user).all()
    shelves = Shelf.query.filter_by(owner=user).all()
    updates = reviews + [bookInShelf for shelf in shelves for bookInShelf in shelf.books]
    return updates


def get_updates(users):
    updates = []
    for user in users:
        updates += get_user_updates(user)
    updates.sort(key=lambda update: update.date_posted, reverse=True)
    return updates


def get_event(event_type, event_id):
    if event_type == 'like':
        return UserLikedReview.query.get(event_id)
    return UserCommentedReview.query.get(event_id)
