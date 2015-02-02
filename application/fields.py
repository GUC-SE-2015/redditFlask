"""
Here we define marshaling, which map python dicts to JSON
"""
from flask.ext.restful import fields

user_fields = {
    'id': fields.String,
    'username' : fields.String,
    'url': fields.Url(endpoint='user_ep')
}

token_fields = {
    "token": fields.String,
    "expires_in": fields.Integer
}