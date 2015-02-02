"""
Here we define how to parse JSON parameters sent by the client
"""
from flask.ext.restful import reqparse


user_parser = reqparse.RequestParser()
user_parser.add_argument('username', str)
user_parser.add_argument('password', str)

token_parser = reqparse.RequestParser()
token_parser.add_argument('expires_in', type=int, default=60)