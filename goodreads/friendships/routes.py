from flask_login import login_required, current_user
from flask import (request, abort, Blueprint, jsonify)
from goodreads.models import FriendRequest, Friendship
from goodreads import db


friendships = Blueprint('friendships', __name__)


@friendships.route("/friendship/new")
@login_required
def create_friendship():
    friend_request_id = request.args.get('friend_request_id')
    friend_request = FriendRequest.query.get_or_404(friend_request_id)
    sender = friend_request.sender
    receiver = friend_request.receiver
    if (current_user != receiver):
        abort(403)
    friendship = Friendship(user=sender, friend=receiver)
    twin_friendship = Friendship(user=receiver, friend=sender)
    db.session.add(friendship)
    db.session.add(twin_friendship)
    db.session.delete(friend_request)
    db.session.commit()
    fs = next((fs for fs in sender.friends if fs.friend == receiver), None)
    return jsonify(friendship_id=fs.id)


@friendships.route("/friendship/delete")
@login_required
def remove_friendship():
    friendship_id = request.args.get('friendship_id')
    friendship = Friendship.query.get_or_404(friendship_id)
    if current_user != friendship.user and current_user != friendship.friend:
        abort(403)
    user = friendship.user
    friend = friendship.friend
    twin_friendship = next((fs for fs in user.friend_of if fs.user == friend), None)
    db.session.delete(friendship)
    db.session.delete(twin_friendship)
    db.session.commit()
    return jsonify()
