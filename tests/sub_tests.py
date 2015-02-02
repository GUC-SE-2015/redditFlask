"""
Basic subreddit tests
"""
import base64
import json
from application import api, db
from application.resources import *



class TestSubreddit(object):
    def setUp(self):
        """Creates tables before test cases"""
        from application.models import User
        api.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        db.create_all()
        self.user_one = User(username="subuser1", password="password")
        self.user_two = User(username="subuser2", password="password")
        db.session.add(self.user_one)
        db.session.add(self.user_two)
        db.session.commit()
    def tearDown(self):
        """Clear db after a test"""
        db.session.remove()
        db.drop_all()

    @staticmethod
    def create_auth(user):
        x_auth = "{0}:{1}".format(user.username, "password")
        x_auth = base64.b64encode(x_auth)
        return x_auth

    def get_token_header(self, user):
        x_auth = self.create_auth(user)
        response = self.app.post('/tokens', headers={'X-Auth': x_auth})
        return {"X-Auth-Token": json.loads(response.data)['token']}

    def testCreateSubreddit(self):
        data = {
           "name": "funny"
        }
        headers = self.get_token_header(self.user_one)
        response = self.app.post('/subreddits', data=data, headers=headers)
        assert response.status_code == 201
        response = self.app.get('/subreddits')
        assert response.status_code == 200
        assert len(json.loads(response.data)) == 1
        response = self.app.get('/user/{0}'.format(self.user_one.username))
        rdata = json.loads(response.data)
        assert len(rdata['subscriptions']) == 1

    def testSubscribe(self):
        data = {
           "name": "funny"
        }
        headers = self.get_token_header(self.user_two)
        response = self.app.post('/subreddits', data=data, headers=headers)
        headers = self.get_token_header(self.user_two)
        response = self.app.post('/r/funny/subscribe', headers=headers)
        assert response.status_code == 201
        response = self.app.get('/user/{0}'.format(self.user_two.username))
        rdata = json.loads(response.data)
        assert len(rdata['subscriptions']) == 1
        response = self.app.delete('/r/funny/subscribe', headers=headers)
        assert response.status_code == 200
        response = self.app.get('/user/{0}'.format(self.user_two.username))
        rdata = json.loads(response.data)
        assert len(rdata['subscriptions']) == 0
