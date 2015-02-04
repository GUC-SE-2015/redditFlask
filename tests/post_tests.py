import base64
import json
from application import api, db
from application.resources import *
from application.models import User


class TestPosts(object):

    @staticmethod
    def create_auth(user):
        x_auth = "{0}:{1}".format(user.username, "password")
        x_auth = base64.b64encode(x_auth)
        return x_auth

    def get_token_header(self, user):
        x_auth = self.create_auth(user)
        response = self.app.post('/tokens', headers={'X-Auth': x_auth})
        return {"X-Auth-Token": json.loads(response.data)['token']}

    def setUp(self):
        """Creates tables before test cases"""
        from application.models import User
        api.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        api.app.config['TESTING'] = True
        self.app = api.app.test_client()
        db.create_all()
        self.user = User(username="subuser1", password="password")
        db.session.add(self.user)
        db.session.commit()
        data = {
            "name": "funny"
        }
        self.headers = self.get_token_header(self.user)
        self.app.post('/subreddits', data=data, headers=self.headers)

    def tearDown(self):
        """Clear db after a test"""
        db.session.remove()
        db.drop_all()

    def testCreatePosts(self):
        data = {
            "title": "Test post please ignore",
            "body": "This is a test post, please ignore it."
        }
        response = self.app.get('/r/funny')
        rdata = json.loads(response.data)
        assert len(rdata['posts']) == 0
        response = self.app.post('/r/funny', data=data, headers=self.headers)
        assert response.status_code == 200
        rdata = json.loads(response.data)
        assert rdata['author'] == self.user.username
        assert rdata['upvotes'] == 1
        assert rdata['downvotes'] == 0
        assert rdata['myvote'] == 1
        response = self.app.get('/r/funny')
        rdata = json.loads(response.data)
        assert len(rdata['posts']) == 1

    def testVotes(self):
        data = {
            "title": "Test post please ignore",
            "body": "This is a test post, please ignore it."
        }
        response = self.app.post('/r/funny', data=data, headers=self.headers)
        rdata = json.loads(response.data)
        post_url = rdata['url']
        post_up_url = rdata['upvote_url']
        post_down_url = rdata['downvote_url']
        downvoter = User(username='brokenarms', password="password")
        db.session.add(downvoter)
        db.session.commit()
        headers = self.get_token_header(downvoter)
        # First downvote
        response = self.app.post(post_down_url, headers=headers)
        assert response.status_code == 201
        response = self.app.get(post_url)
        assert json.loads(response.data)['downvotes'] == 1
        assert json.loads(response.data)['upvotes'] == 1
        assert json.loads(response.data)['myvote'] == 0
        response = self.app.get('/u/{0}'.format(self.user.username))
        assert json.loads(response.data)['karma'] == 0
        # Remove downvote
        response = self.app.delete(post_down_url, headers=headers)
        assert response.status_code == 204
        # upvote
        response = self.app.post(post_up_url, headers=headers)
        assert response.status_code == 201
        response = self.app.get('/u/{0}'.format(self.user.username))
        rdata = json.loads(response.data)
        assert rdata['karma'] == 2
        response = self.app.get(post_url)
        rdata = json.loads(response.data)
        assert rdata['upvotes'] == 2
        assert rdata['downvotes'] == 0
        response = self.app.get('/u/{0}'.format(self.user.username))
        assert json.loads(response.data)['karma'] == 2

    def testComment(self):
        data = {
            "title": "Test post please ignore",
            "body": "This is a test post, please ignore it."
        }
        response = self.app.post('/r/funny', data=data, headers=self.headers)
        rdata = json.loads(response.data)
        post_url = rdata['url']
        data = {
            "body": "This is a test body please ignore"
        }
        response = self.app.post(post_url, data=data, headers=self.headers)
        rdata = json.loads(response.data)
        assert response.status_code == 201
        assert rdata['upvotes'] == 1
        assert rdata['downvotes'] == 0
        response = self.app.get('/u/{0}'.format(self.user.username))
        rdata = json.loads(response.data)
        assert rdata['karma'] == 2
