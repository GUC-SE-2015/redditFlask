"""
Here we define marshaling, which map python dicts to JSON
"""
from flask.ext.restful import fields


subreddit_fields = {
    "name": fields.String,
    'url': fields.Url(endpoint='subreddit_ep'),
    'subscription_url': fields.Url(endpoint='subreddit_subscription_ep')
}

user_fields = {
    'id': fields.String,
    'username' : fields.String,
    'subscriptions': fields.List(fields.Nested(subreddit_fields)),
    'url': fields.Url(endpoint='user_ep')
}

token_fields = {
    "token": fields.String,
    "expires_in": fields.Integer
}

