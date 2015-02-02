"""
Here we define how to parse JSON parameters sent by the client
"""
from flask.ext.restful import reqparse


user_parser = reqparse.RequestParser()
user_parser.add_argument('username', str)
user_parser.add_argument('password', str)

token_parser = reqparse.RequestParser()
token_parser.add_argument('expires_in', type=int, default=60)

subreddit_parser = reqparse.RequestParser()
subreddit_parser.add_argument('name', str)

post_parser = reqparse.RequestParser()
post_parser.add_argument('title', str)
post_parser.add_argument('body', str)


comment_parser = reqparse.RequestParser()
comment_parser.add_argument('body', str)