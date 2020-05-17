from flask import (render_template, url_for, flash,
                   redirect, abort, Blueprint)
from flask_login import login_required, current_user
from goodreads.messages.forms import MessageForm
from goodreads.models import Message, User
from goodreads import db

messages = Blueprint('messages', __name__)


@messages.route("/messages/new/<string:receiver_id>", methods=['GET', 'POST'])
@login_required
def create_message(receiver_id):
    form = MessageForm()
    receiver = User.query.get_or_404(receiver_id)
    if form.validate_on_submit():
        message = Message(title=form.title.data, content=form.content.data,
                          sender=current_user, receiver=receiver)
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_message.html', form=form, receiver=receiver, legend='New Message')


@messages.route("/messages/<int:message_id>")
@login_required
def message(message_id):
    message = Message.query.get_or_404(message_id)
    return render_template('message.html', message=message)


@messages.route("/messages")
@login_required
def my_messages():
    messages_sent = current_user.messages_sent
    messages_received = current_user.messages_received
    messages_sent.sort(key=lambda message: message.date_posted, reverse=True)
    messages_received.sort(key=lambda message: message.date_posted, reverse=True)
    return render_template('messages.html', messages_sent=messages_sent, messages_received=messages_received)


@messages.route("/messages/<int:message_id>/delete", methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your message has been deleted!', 'success')
    return redirect(url_for('main.home'))
