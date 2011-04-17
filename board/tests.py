#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Paul Bagwell on 2011-03-26.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.utils import unittest
from django.test.client import Client
from board import models

"""
We load some fixtures and start with this information:
Post.objects.count() == 100
Thread.objects.count() == 10
Section.objects.count() == ~40
SectionGroup.objects.count() == 6
FileType.objects.count() == 35

"""

USERNAME = 'paul'
PASSWORD = 'paulpaul'


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_post_create(self):
        response = self.client.post('/api/post/', {
            'poster': '',
            'email': '',
            'topic': '',
            'message': 'Test message',
            'section': 'fd',  # this section has 'force_files': false
            'recaptcha_challenge_field': '',
            'recaptcha_response_field': '',
            'password': 'R1Iet7uL',
        })
        self.assertEqual(response.status_code, 201)  # HTTP_CREATED
        self.assertEqual(response.content, '{"id": 1}')  # response body
        posts = models.Post.objects.all()
        self.assertEqual(posts.count(), 1)
        post = posts.get()
        self.assertEqual(post.values(), 'json')

        # TODO: test comet

    def test_post_delete(self):
        post_id = 1
        url = '/api/post/{0}'.format(post_id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)  # HTTP DELETED
        self.assertFalse(response.content)  # shouldn't return anything
        p = Post.objects.get(id=post_id)
        self.assertTrue(p.is_deleted)
        self.assertEqual(p.thread.section.pid, 101)

        # Test
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
