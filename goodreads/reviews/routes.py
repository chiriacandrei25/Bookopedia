from flask_login import login_required, current_user
from flask import (render_template, url_for, request, redirect, abort, Blueprint, jsonify)
from goodreads.reviews.forms import ReviewForm
from goodreads.models import Book, Review, UserLikedReview, UserCommentedReview
from goodreads.notifications.utils import remove_like_notification
from goodreads.reviews.utils import remove_review_likes, remove_review_comments
from goodreads import db


reviews = Blueprint('reviews', __name__)


@reviews.route("/review/new/<int:book_id>")
@login_required
def create_review(book_id):
    my_review = next((review for review in current_user.reviews if review.book_id == book_id), None)
    if my_review is not None:
        return redirect(url_for('reviews.update_review', review_id=my_review.id))
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()
    return render_template('create_review.html', form=form, book=book, legend='New review')


@reviews.route("/review/new")
@login_required
def new_review():
    book_id = request.args.get('book_id')
    book = Book.query.get_or_404(book_id)
    rating = request.args.get('rating')
    review = request.args.get('review')
    form = ReviewForm(rating=rating, review=review)
    if form.validate():
        review = Review(user=current_user, book=book, rating=form.rating.data, review=form.review.data)
        db.session.add(review)
        book.reviews.append(review)
        current_user.reviews.append(review)
        db.session.commit()
        return jsonify(valid_review="True", redirect=url_for('books.book', book_id=book_id))
    return jsonify(valid_review="False", rating_errors=render_template('rating_errors.html', form=form))


@reviews.route("/review/delete")
@login_required
def delete_review():
    with db.session.no_autoflush:
        review_id = request.args.get('review_id')
        review = Review.query.get_or_404(review_id)
        if review.user != current_user:
            abort(403)
        book = review.book
        remove_review_likes(review)
        remove_review_comments(review)
        db.session.delete(review)
        db.session.commit()
        return jsonify(result=render_template('book_reviews.html', book=book))


@reviews.route("/review/<int:review_id>", methods=['GET', 'POST'])
def review(review_id):
    review = Review.query.get_or_404(review_id)
    return render_template('review.html', review=review)


@reviews.route("/review/<int:review_id>/update")
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user != current_user:
        abort(403)
    form = ReviewForm()
    form.review.data = review.review
    return render_template('update_review.html', form=form, review=review)


@reviews.route("/review/edit")
@login_required
def edit_review():
    review_id = request.args.get('review_id')
    review = Review.query.get_or_404(review_id)
    new_rating = request.args.get('rating')
    new_review = request.args.get('review')
    form = ReviewForm(rating=new_rating, review=new_review)
    if form.validate():
        review.rating = form.rating.data
        review.review = form.review.data
        db.session.commit()
        return jsonify(valid_review="True", redirect=url_for('books.book', book_id=review.book.id))
    return jsonify(valid_review="False", rating_errors=render_template('rating_errors.html', form=form))


@reviews.route("/review/like")
@login_required
def like_review():
    review_id = request.args.get('review_id')
    review = Review.query.get_or_404(review_id)
    like = UserLikedReview(user=current_user, review=review)
    db.session.add(like)
    review.likes.append(like)
    db.session.commit()
    return jsonify(likes_count=len(review.likes),
                   likes_container=render_template("likes_container.html", review=review),
                   like_id=like.id)


@reviews.route("/review/unlike")
@login_required
def unlike_review():
    review_id = request.args.get('review_id')
    review = Review.query.get_or_404(review_id)
    my_like_id = next((like.id for like in review.likes if like.user == current_user), None)
    my_like = UserLikedReview.query.get(my_like_id)
    remove_like_notification(my_like)
    db.session.delete(my_like)
    db.session.commit()
    return jsonify(likes_count=len(review.likes),
                   likes_container=render_template("likes_container.html", review=review))


@reviews.route("/review/comment")
@login_required
def comment_review():
    review_id = request.args.get('review_id')
    comment = request.args.get('comment')
    review = Review.query.get_or_404(review_id)
    comment = UserCommentedReview(user=current_user, review=review, comment=comment)
    review.comments.append(comment)
    db.session.commit()
    return jsonify(comments_count=len(review.comments),
                   comment_template=render_template('comment.html', comment=comment))


@reviews.route("/review/comments")
def review_comments():
    review_id = request.args.get('review_id')
    review = Review.query.get_or_404(review_id)
    comments_count = int(request.args.get('comments_count'))
    comments = review.comments[:comments_count + 10]
    return jsonify(comments_container=render_template('review_comments.html', comments=comments))
