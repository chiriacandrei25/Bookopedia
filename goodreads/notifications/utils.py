from goodreads.models import Notification
from goodreads import db


def remove_like_notification(like):
    notifications = Notification.query.all()
    notification_id = next((notif.id for notif in notifications
                            if notif.event_type == 'like' and notif.event_id == like.id), None)
    notification = Notification.query.get(notification_id)
    if notification is not None:
        db.session.delete(notification)
        db.session.commit()


def remove_comment_notification(comment):
    notifications = Notification.query.all()
    notification_id = next((notif.id for notif in notifications
                            if notif.event_type == 'comment' and notif.event_id == comment.id), None)
    notification = Notification.query.get(notification_id)
    if notification is not None:
        db.session.delete(notification)
        db.session.commit()
