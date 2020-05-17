from goodreads import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy_serializer import SerializerMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)
    shelves = db.relationship('Shelf', backref='owner', lazy=True)
    requests_sent = db.relationship('FriendRequest', foreign_keys='FriendRequest.sender_id',
                                    backref='sender', lazy=True)
    requests_received = db.relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id',
                                        backref='receiver', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    friends = db.relationship('Friendship', foreign_keys='Friendship.user_id', backref='user', lazy=True)
    friend_of = db.relationship('Friendship', foreign_keys='Friendship.friend_id', backref='friend', lazy=True)
    liked_reviews = db.relationship('UserLikedReview', back_populates='user', cascade="all, delete-orphan")
    review_comments = db.relationship('UserCommentedReview', back_populates='user', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True)
    unseen_notifications = db.Column(db.Integer, default=0)

    def get_latest_notifications(self):
        notifs = self.notifications
        notifs.reverse()
        return notifs

    def reset_unseen_notifications(self):
        self.unseen_notifications = 0

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.first_name}')"


class Shelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('BookInShelf', back_populates='shelf', cascade="all, delete-orphan")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="Yet to come.")
    publisher = db.Column(db.String(1000))
    publication_date = db.Column(db.DateTime)
    page_count = db.Column(db.Integer)
    image_url = db.Column(db.String(100), nullable=False)
    small_image_url = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='book', lazy=True)
    shelves = db.relationship('BookInShelf', back_populates='book', cascade="all, delete-orphan")
    authors = db.relationship('AuthorBookLink', back_populates='book', cascade="all, delete-orphan")


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    small_image_url = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    big_image_url = db.Column(db.String(100))
    about = db.Column(db.Text)
    born_at = db.Column(db.String(20))
    died_at = db.Column(db.String(20))
    hometown = db.Column(db.String(100))
    books = db.relationship('AuthorBookLink', back_populates='author', cascade="all, delete-orphan")


class AuthorBookLink(db.Model):  #link between Author and Book
    __tablename__ = 'author_book_link'
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    author_role = db.Column(db.String(50))
    author = db.relationship('Author', back_populates='books')
    book = db.relationship('Book', back_populates='authors')


class BookInShelf(db.Model):  #link between Book and Shelf
    __tablename__ = 'book_in_shelf'
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), primary_key=True)
    shelf_id = db.Column(db.Integer, db.ForeignKey('shelf.id'), primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    book = db.relationship('Book', back_populates='shelves')
    shelf = db.relationship('Shelf', back_populates='books')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text)


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)


class UserLikedReview(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    user = db.relationship('User', back_populates='liked_reviews')
    review = db.relationship('Review', back_populates='likes')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)


class UserCommentedReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    user = db.relationship('User', back_populates='review_comments')
    review = db.relationship('Review', back_populates='comments')
    comment = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    event_type = db.Column(db.String(30), nullable=False)
    event_id = db.Column(db.Integer)

    def get_event(self):
        if self.event_type == 'like':
            return UserLikedReview.query.get(self.event_id)
        return UserCommentedReview.query.get(self.event_id)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    likes = db.relationship('UserLikedReview', back_populates='review', cascade="all, delete-orphan")
    comments = db.relationship('UserCommentedReview', back_populates='review', cascade="all, delete-orphan")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
