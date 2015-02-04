"""
Here we define marshaling, which map python dicts to JSON
"""
from flask.ext.restful import fields

comment_fields = {
    "id": fields.String,
    "body": fields.String,
    "upvotes": fields.Integer,
    "downvotes": fields.Integer,
    "myvote": fields.Integer,
    "upvote_url": fields.Url(endpoint="upvote_ep"),
    "downvote_url": fields.Url(endpoint="downvote_ep"),
    'url': fields.Url(endpoint='comment_ep')
}

post_fields = {
    "id": fields.String,
    "title": fields.String,
    "body": fields.String,
    "author": fields.String,
    "upvotes": fields.Integer,
    "myvote": fields.Integer,
    "downvotes": fields.Integer,
    "comments": fields.List(fields.Nested(comment_fields)),
    "upvote_url": fields.Url(endpoint="upvote_ep"),
    "downvote_url": fields.Url(endpoint="downvote_ep"),
    'url': fields.Url(endpoint='post_ep')
}

subreddit_fields = {
    "name": fields.String,
    'url': fields.Url(endpoint='subreddit_ep'),
    "posts": fields.List(fields.Nested(post_fields)),
    'subscription_url': fields.Url(endpoint='subreddit_subscription_ep')
}

user_fields = {
    'id': fields.String,
    'username' : fields.String,
    'subscriptions': fields.List(fields.Nested(subreddit_fields)),
    "posts": fields.List(fields.Nested(post_fields)),
    "comments": fields.List(fields.Nested(comment_fields)),
    "karma": fields.Integer,
    'url': fields.Url(endpoint='user_ep')
}

token_fields = {
    "token": fields.String,
    "expires_in": fields.Integer
}

