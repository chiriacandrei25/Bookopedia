from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from goodreads import db, bcrypt
from goodreads.models import User, Shelf
from goodreads.users.utils import send_reset_email
from goodreads.shelves.forms import ShelfForm
from goodreads.utils import save_picture, get_updates
from goodreads.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        read = Shelf(owner=user, name='read')
        db.session.add(read)
        to_read = Shelf(owner=user, name='to-read')
        db.session.add(to_read)
        currently_reading = Shelf(owner=user, name='currently-reading')
        db.session.add(currently_reading)
        user.shelves.extend([read, to_read, currently_reading])
        db.session.commit()
        flash('Your account has been created! You are able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful.')
    return render_template('login.html', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data, 'static/pics/profile_pics')
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account info has been updated.', 'success')
        redirect(url_for('users.account'))
    else:
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    image_file = url_for('static', filename='/pics/profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)


@users.route('/user/<string:user_id>')
def user_page(user_id):
    user = User.query.get_or_404(user_id)
    form = ShelfForm()
    relationship = 'none'
    friendship_id = 0
    if current_user.is_authenticated:
        friendship = next((fr for fr in current_user.friends if fr.friend == user), None)
        if friendship is not None:
            relationship = 'friends'
            friendship_id = friendship.id
        else:
            request_sent = next((fr for fr in current_user.requests_sent if fr.receiver == user), None)
            if request_sent is not None:
                relationship = 'request_sent'
                friendship_id = request_sent.id
            else:
                request_received = next((fr for fr in current_user.requests_received if fr.sender == user), None)
                if request_received is not None:
                    relationship = 'request_received'
                    friendship_id = request_received.id
    user_updates = get_updates([user])
    return render_template('user_page.html', relationship=relationship, friendship_id=friendship_id,
                           form=form, user=user, updates=user_updates)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed! You are able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', form=form, user=user)


@users.route('/reset_unseen_notifications')
@login_required
def reset_unseen_notifications():
    current_user.reset_unseen_notifications()
    db.session.commit()
    return jsonify()
