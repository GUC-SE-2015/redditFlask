"""
Main application package.
In this file we define our app and api.
"""
from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy # Our ORM
app = Flask(__name__) # Initialize flask application
app.config.from_object('config') # Configure from a python module
db = SQLAlchemy(app)

# We are using Flask-Restful extension to provide some convenient functionality
# For creating restful apis
# WE need to initialize that as well
api = Api(app, catch_all_404s=True)