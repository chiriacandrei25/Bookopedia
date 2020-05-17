from goodreads.models import UserLikedReview, UserCommentedReview
from goodreads import db
from goodreads.notifications.utils import remove_like_notification, remove_comment_notification


def remove_review_likes(review):
    likes = UserLikedReview.query.filter_by(review=review)
    for like in likes:
        remove_like_notification(like)
        db.session.delete(like)


def remove_review_comments(review):
    comments = UserCommentedReview.query.filter_by(review=review)
    for comment in comments:
        remove_comment_notification(comment)
        db.session.delete(comment)
