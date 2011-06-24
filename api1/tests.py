from urllib import quote_plus as quote

from django.utils import unittest
from django.test.client import Client

from board.models import Post

USERNAME = "paul"
PASSWORD = "paulpaul"
API_URL = "/api/1.0"


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_post_create(self):
        data = {
            "message": "Test message",
            "section": "fd",  # this section has "force_files": false
            "password": PASSWORD,
        }
        # POST should return HTTP 201 Created.
        response = self.client.post(API_URL + "/post/", data)
        assert response.status_code == 201, response.status_code
        # Assuming the currently created post is the only one in the database.
        posts = Post.objects.all()
        assert posts.count() == 1, "try to reset the db first"
        # This post object should contain exactly same values
        # as specified in the {data} dict.
        post = posts.values()[0]
        assert post["message"] == data["message"], post["message"]

    def test_post_delete(self):
        # NOTE: need to call test_post_create first.
        # NOTE: PASSWORD must not change between those tests.
        post_id = 1
        url = API_URL + "/post/{}?password={}".format(post_id, quote(PASSWORD))
        # DELETE should return HTTP 200 OK with no body.
        response = self.client.delete(url)
        assert response.status_code == 200, response.status_code
        assert not response.content
        # The post itself must remain in the database with is_deleted
        # field set to True.
        p = Post.deleted_objects.get(id=post_id)
        assert p.is_deleted
        # The remote client should not be able to retrieve it, though.
        response = self.client.get(url)
        assert response.status_code == 404, response.status_code

    def test_user_post_delete(self):
        # Create a new user "test" which should be able to remove
        # the post created in test_post_create()
        params = {"username": "test", "password": "test"}
        User(**params).save()
        self.client = Client()
        self.client.login(**params)
        self.test_post_delete()

    def test_feed(self):
        # TODO:
        # * Adding to the feed on post creation
        # * Adding to the feed on thread creation
        # * Adding to the feed on bookmark button click
        pass
