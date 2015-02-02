"""
We define all of our models here
"""
from . import db, app
from flask.ext.bcrypt import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature

# Secondary table for subscriptions
subscriptions = db.Table('subscriptions',
    db.Column('user_username', db.String(256), db.ForeignKey('user.username')),
    db.Column('subreddit_name', db.String(256), db.ForeignKey('subreddit.name'))
    )

class User(db.Model):

    """
    We are using username as primary_key here for semantic sense.
    However it is important to note that using autogenerated integers make index
    maintenence much easier.
    """
    username = db.Column(db.String(256), primary_key=True)
    password_hash = db.Column(db.String(60), unique=True, nullable=False)

    def __init__(self, username=None, password=None):
        self.username = username
        if password is not None:
            self.password = password
        super(User, self).__init__()

    def to_dict(self):
        return {
            "username": self.username,
            "subscriptions": [ s.to_dict() for s in self.subscriptions]
        }

    @property
    def password(self):
        """Returns hash, not actual password."""
        return self.password_hash

    @password.setter
    def password(self, value):
        """Hashes password."""
        self.password_hash = generate_password_hash(value, 12)

    def verify_pass(self, password):
        """Checks if a password matches the stored hash"""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in):
        """
        Creates an expiring token that can identify this user.
        expires_in is expiration in minutes.
        """
        serializer = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'], expires_in=expires_in * 60)
        return serializer.dumps({'username': self.username})

    @staticmethod
    def verify_auth_token(token):
        """
        Retrieves user who is identified by this token.
        Raises SignatureExpired, BadSignature if expired or malformed.
        """
        serializer = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        data = serializer.loads(token)
        user = User.query.get(data['username'])
        if user is None:
            raise BadSignature("Could not identify owner.")
        return user

class Subreddit(db.Model):
    name = db.Column(db.String(256), primary_key=True)
    subscribers = db.relationship('User', secondary=subscriptions, backref=db.backref('subscriptions'))

    def __init__(self, name=None):
        self.name = name
        super(Subreddit, self).__init__()

    def to_dict(self):
        return {
            "name": self.name
        }