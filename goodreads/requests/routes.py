from flask_login import login_required, current_user
from flask import (request, abort, Blueprint, jsonify, render_template)
from goodreads.models import User, FriendRequest
from goodreads import db


requests = Blueprint('requests', __name__)


@requests.route("/request/new")
@login_required
def create_request():
    sender_id = request.args.get('sender_id')
    sender = User.query.get_or_404(sender_id)
    receiver_id = request.args.get('receiver_id')
    receiver = User.query.get_or_404(receiver_id)
    print(sender_id, receiver_id)
    if sender == receiver or current_user != sender or \
       receiver in [fs.friend for fs in sender.friends] or \
       sender in [req.sender for req in receiver.requests_received] or \
       sender in [req.receiver for req in receiver.requests_sent]:
        abort(403)
    friendRequest = FriendRequest(sender=sender, receiver=receiver)
    db.session.add(friendRequest)
    db.session.commit()
    friendRequest = next((fr for fr in sender.requests_sent if fr.receiver == receiver), None)
    return jsonify(friend_request_id=friendRequest.id)


@requests.route("/request/delete")
@login_required
def remove_request():
    friend_request_id = request.args.get('friend_request_id')
    friend_request = FriendRequest.query.get_or_404(friend_request_id)
    if (current_user != friend_request.sender and current_user != friend_request.receiver):
        abort(403)
    db.session.delete(friend_request)
    db.session.commit()
    requests_sent = current_user.requests_sent
    requests_received = current_user.requests_received
    requests_sent.sort(key=lambda message: message.date_posted, reverse=True)
    requests_received.sort(key=lambda message: message.date_posted, reverse=True)
    return jsonify(result=render_template('requests.html', requests_sent=requests_sent,
                   requests_received=requests_received))


@requests.route("/request/friend_requests")
@login_required
def friend_requests():
    requests_sent = current_user.requests_sent
    requests_received = current_user.requests_received
    requests_sent.sort(key=lambda message: message.date_posted, reverse=True)
    requests_received.sort(key=lambda message: message.date_posted, reverse=True)
    return render_template('requests.html', requests_sent=requests_sent, requests_received=requests_received)
