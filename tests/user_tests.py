"""
Test cases for user functionality.
"""
import base64
import json
from application import api, db
from application.resources import *


class TestRegistration(object):

    def setUp(self):
        """Create tables before test cases"""
        api.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        db.create_all()

    def tearDown(self):
        """Clear db after a test"""
        db.session.remove()
        db.drop_all()

    def testRegistration(self):
        post_data = {
            "username": "Some User",
            "password": "12345678"
        }
        response = self.app.post('/users', data=post_data)
        assert response.status_code == 201
        response = self.app.get('/users')
        assert len(json.loads(response.data)) == 1


class TestLogin(object):

    def setUp(self):
        """Creates tables before test cases"""
        from application.models import User
        api.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        db.create_all()
        self.user = User(username="logintester", password="password")
        db.session.add(self.user)
        db.session.commit()

    @staticmethod
    def create_auth(username, password):
        x_auth = "{0}:{1}".format(username, password)
        x_auth = base64.b64encode(x_auth)
        return x_auth

    def testCreateToken(self):
        x_auth = self.create_auth(self.user.username, "password")
        response = self.app.post('/tokens', headers={'X-Auth': x_auth})
        assert response.status_code == 201
        # Default expiration is 60 minutes
        assert json.loads(response.data)['expires_in'] == 60

    def testChangePass(self):
        x_auth = self.create_auth(self.user.username, "password")
        response = self.app.post('/tokens', headers={'X-Auth': x_auth})
        headers = {
            "X-Auth-Token": json.loads(response.data)['token']
        }
        data = {
            "password": "12345678"
        }
        response = self.app.put(
            '/user/{0}'.format(self.user.username), data=data, headers=headers)
        assert response.status_code == 200
        x_auth = self.create_auth(self.user.username, "12345678")
        response = self.app.post('/tokens', headers={'X-Auth': x_auth})
        assert response.status_code == 201

    def tearDown(self):
        """Clear db after a test"""
        db.session.remove()
        db.drop_all()
