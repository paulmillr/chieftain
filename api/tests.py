#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Paul Bagwell on 2011-04-25.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from nose.tools import eq_
from urllib import urlencode
from django.utils import unittest
from django.test.client import Client
from board.models import Post

USERNAME = 'paul'
PASSWORD = 'paulpaul'


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_post_create(self):
        data = {
            'message': 'Test message',
            'section': 'fd',  # this section has 'force_files': false
            'password': PASSWORD,
        }
        response = self.client.post('/api/post/', data)
        eq_(response.status_code, 201)   # HTTP_CREATED
        posts = Post.objects.all()
        eq_(posts.count(), 1)
        post = posts.values()[0]
        eq_(post['message'], data['message'])

    def test_post_delete(self):
        post_id = 1
        params = urlencode({'password': PASSWORD})
        url = '/api/post/{0}?{1}'.format(post_id, params)
        response = self.client.delete(url)
        eq_(response.status_code, 200)
        assert not response.content
        p = Post.deleted_objects.get(id=post_id)
        assert p.is_deleted
        response = self.client.get(url)
        eq_(response.status_code, 404)
