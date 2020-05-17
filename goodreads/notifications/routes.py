from flask_login import login_required, current_user
from flask import (request, Blueprint, jsonify, render_template)
from goodreads.models import User, Notification
from goodreads import db, socketio
from goodreads.utils import get_event
from flask_socketio import send, emit


notifications = Blueprint('notifications', __name__)


@notifications.route("/notifications/new")
@login_required
def create_notification():
    event_type = request.args.get('event_type')
    event_id = request.args.get('event_id')
    event = get_event(event_type, event_id)
    user = User.query.get_or_404(event.review.user.id)
    user.unseen_notifications += 1
    notification = Notification(event_type=event_type, event_id=event_id, user=user)
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification_id=notification.id)


@notifications.route("/notifications")
@login_required
def my_notifications():
    notifications = current_user.notifications
    notifications.sort(key=lambda notification: notification.timestamp, reverse=True)
    return render_template('notifications.html', notifications=notifications)


@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)


@socketio.on('notification')
def handleNotification(json):
    print("Pula")
    notification_id = json.get('notification_id')
    notification = Notification.query.get(notification_id)
    event = get_event(notification.event_type, notification.event_id)
    if notification.event_type == 'like':
        content = render_template('notification_card.html', user=event.user, event=event,
                                  content=' liked your review: ' + event.review.review)
        print(content)
        emit('add_notification', {'user_id': event.user.id,
                                  'receiver_id': event.review.user_id,
                                  'content': content}, broadcast=True)
    else:
        content = render_template('notification_card.html', user=event.user, event=event,
                                  content=' commented on your review: ' + event.review.review)
        emit('add_notification', {'user_id': event.user.id,
                                  'receiver_id': event.review.user_id,
                                  'content': content}, broadcast=True)
    '''
    user = User.query.get(user_id)
    review_id = json.get('review_id')
    action = json.get('action')
    review = Review.query.get(review_id)
    msg = user.first_name + ' ' + action
    '''
