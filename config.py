"""
Configuration for our flask application.
Variables defined here will be accessible through the app.config dictionary.
"""
DEBUG = False
SECRET_KEY = "123?"
SQLALCHEMY_DATABASE_URI = "sqlite:///flaskReddit.db"