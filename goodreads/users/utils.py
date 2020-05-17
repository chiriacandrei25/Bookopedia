from flask import url_for
from goodreads import mail
from goodreads.models import Book
from goodreads.books import get_sim_matrix
from flask_mail import Message


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Resset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                    {url_for('users.reset_password', token=token, _external=True)}
                    If you did not make this request then simply ignore this email and no changes will be made.
                '''
    mail.send(msg)


def get_user_ratings(user):
    ratings = [0] * 1900
    for review in user.reviews:
        if review.book_id <= 1900:
            ratings[review.book_id - 1] = review.rating
    return ratings


def predict_rating(user_ratings, book_id, sim_matrix):
    neighbors = []
    for i in range(0, 1900):
        if i != book_id:
            neighbors.append((sim_matrix[i][book_id - 1], user_ratings[i]))

    neighbors.sort(reverse=True)
    k_neighbors = neighbors[:40]
    sum_sim = sum_ratings = actual_k = 0
    for (sim, r) in k_neighbors:
        if sim > 0:
            sum_sim += sim
            sum_ratings += sim * r
            actual_k += 1
    if actual_k < 1:
        return 0
    return sum_ratings / sum_sim


def user_recommended_books(user):
    user_ratings = get_user_ratings(user)
    sim_matrix = get_sim_matrix(True)
    book_ids = []
    for book_id in range(1, 1900):
        if book_id not in [review.book_id for review in user.reviews]:
            book_ids.append(book_id)
    book_ids.sort(key=lambda book_id: predict_rating(user_ratings, book_id, sim_matrix), reverse=True)
    return [Book.query.get(book_id) for book_id in book_ids[:10]]
