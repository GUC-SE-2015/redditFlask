from flask.ext.restful import Resource, marshal_with, abort
from . import db, api
from flask import g, request
from fields import user_fields, token_fields, subreddit_fields
from parsers import user_parser, token_parser, subreddit_parser
from models import User, BadSignature, SignatureExpired, Subreddit
from functools import wraps
import base64

def token_required(func):
    """
    Sets g.user to currently logged in user accordinf to token.
    Calls abort if expired or invalid token.
    g is a thread local variable provided by flask.
    """
    @wraps(func) # Presrve doc string and other goodies.
    def decorator(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', None)
        if token is None:
            abort(401, message="Please provide X-Auth-Token header.")
        try:
            g.user = User.verify_auth_token(token)
            return func(*args, **kwargs) # Call wraped function
        except BadSignature:
            abort(401, message="Invalid token provided.")
        except SignatureExpired:
            abort(401, message="Token has expired.")
    return decorator


@api.resource('/tokens', endpoint='token_ep')
class TokenResource(Resource):
    """Handle token requests."""
    @marshal_with(token_fields)
    def post(self):
        """
        Creates new tokens.
        """
        auth = request.headers.get('X-Auth', None)
        if auth is None:
            abort(400, message="Missing X-Auth header.")
        try:
            auth = base64.b64decode(auth)
            values = auth.split(':')
            if len(values) != 2:
                abort(400, message="Malformed X-Auth Header.")
            user = User.query.get(values[0])
            if user is None or not user.verify_pass(values[1]):
                abort(401, message="Invalid username or password.")
            args = token_parser.parse_args()
            return {
                "token": user.generate_auth_token(args['expires_in']),
                "expires_in": args["expires_in"]
            }, 201
        except TypeError:
            # Not a base64 string
            abort(400, message="X-Auth must be a base64 string.")

@api.resource('/users', endpoint='users_ep')
class UsersResource(Resource):
    method_decorators = [marshal_with(user_fields)]
    """
    This is the controller for our Users model.
    """

    def get(self):
        """
        Handle HTTP GET method.
        This method lists all users.
        """
        return [u.to_dict() for u in User.query.all()]

    def post(self):
        """
        Handle HTTP POST method.
        Here we create a new user.
        """
        args = user_parser.parse_args()
        if len(args['username']) < 4 or len(args['password']) < 8:
            abort(400, message="Username must be at least four characters long and password must be eight.")
        user = User(username=args['username'], password=args['password'])
        db.session.add(user)
        db.session.commit()
        # HTTP status code 201 to indicate a new entry was created
        return user.to_dict(), 201


@api.resource('/user/<string:username>', endpoint='user_ep')
class UserResource(Resource):
    method_decorators = [marshal_with(user_fields)]

    def get(self, username):
        """
        Handle HTTP GET method.
        Fetches a single user by username
        """
        return User.query.get_or_404(username).to_dict()

    @token_required
    def put(self, username):
        """
        Handles HTTP PUT method.
        Modifies user fields.
        """
        args = user_parser.parse_args()
        if len(args['password']) < 8:
            abort(400, message="Password must be at least eight characters long.")
        g.user.password = args['password'] # There is a gaping security hole here, try to find it out !
        db.session.add(g.user)
        db.session.commit()
        return g.user

@api.resource('/subreddits', endpoint="subreddits_ep")
class SubredditsResource(Resource):
    method_decorators = [marshal_with(subreddit_fields)]

    def get(self):
        """List all subreddits"""
        return [s.to_dict() for s in Subreddit.query.all()]

    @token_required
    def post(self):
        args = subreddit_parser.parse_args()
        if len(args['name']) < 1:
            abort(400, message="Subreddit must have a name.")
        s = Subreddit(name=args['name'])
        s.subscribers.append(g.user)
        db.session.add(s)
        db.session.commit()
        return s.to_dict(), 201

@api.resource('/r/<string:name>', endpoint="subreddit_ep")
class SubredditResource(Resource):
    method_decorators = [marshal_with(subreddit_fields)]

    def get(self, name):
        sub = Subreddit.query.get_or_404(name)
        return sub.to_dict()

@api.resource('/r/<string:name>/subscribe', endpoint="subreddit_subscription_ep")
class SubredditSubscription(Resource):
    method_decorators = [token_required]

    def post(self, name):
        sub = Subreddit.query.get_or_404(name)
        sub.subscribers.append(g.user)
        db.session.add(sub)
        db.session.commit()
        return {"message": "subscribed"}, 201

    def delete(self, name):
        sub = Subreddit.query.get_or_404(name)
        if g.user not in sub.subscribers:
            abort(422, message="You are not subscribed.")
        sub.subscribers.remove(g.user)
        db.session.add(sub)
        db.session.commit()
        return {"message": "unsubscribed"}, 200
