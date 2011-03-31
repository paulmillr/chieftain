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

class ModelsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_thread(self):
        t = Thread.objects.get(id=5)
        self.assertEqual(t.op_post, t.post_set.get(is_op_post=True).values())
        self.assertEqual(t.last_posts, actual, 'message')

        t.remove()
        self.assertTrue(t.is_deleted)
        self.assertTrue(t.op_post.is_deleted)
        self.assertTrue(t.op_post.files()[0].is_deleted)

    def test_post(self):
        p = Post.objects.get(id=50)

        # test post deleting
        p.remove()
        self.assertTrue(p.is_deleted)
        self.assertTrue(p.files().get().is_deleted)

    def test_file(self):
        f = File.objects.get(id=5)
        self.assertEqual(expected, actual, 'message')

        f.remove()
        self.assertTrue(f.is_deleted)

    def test_section(self):
        s = Section.objects.get(slug='b')

        ne = Section.objects.filter(slug='not_exist')
        self.assertRaises(models.Section.DoesNotExist, ne.get)

        last = Post.objects.filter(thread__section=self.id).latest()
        self.assertEqual(s.pid, last.pid)
        self.assertIsInstance(s.allowed_filetypes(), dict)
        self.assertEqual(s.key, 'section_last_b')

    def test_wordfilter(self):
        w = Wordfilter(word=u'тест')
        response = send_post('тест')
        self.assertEqual(response.status_code, 403)

    def test_denied_ip(self):
        d = DeniedIP(ip='127.0.0.1', reason='Test')
        self.assertEqual(self.client.get('/').status_code, 403)


class ViewsTest(unittest.TestCase):
    def setUp(self):
        # init test browser.
        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_board_urls(self):
        def gs(path):
            return self.client.get(path).status_code
        self.assertEqual(gs('/'), 200)
        self.assertEqual(gs('/api/'), 200)
        self.assertEqual(gs('/settings'), 200)
        self.assertEqual(gs('/faq'), 200)
        self.assertEqual(gs('/b/'), 200)
        self.assertEqual(gs('/b/rss'), 200)
        self.assertEqual(gs('/mobile/'), 200)
        self.assertEqual(gs('/pda/'), 200)
        self.assertEqual(gs('/b/1'), 200)
        self.assertEqual(gs('/b/dontexist'), 404)
        self.assertEqual(gs('/b/200'), 404)
        self.assertRedirects(gs('/b/2'), '/b/1#post2', 301)
        self.assertEqual(gs('/dontexist/'), 404)

    def test_login_logout(self):
        c = Client()
        self.assertNotEqual(c.get('/modpanel/').status_code, 200)
        response = c.post('/admin/', {'username': USERNAME, 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(c.get('/modpanel/').status_code, 200)


class APITest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(username=USERNAME, password=PASSWORD)

    def test_thread_create(self):
        response = self.client.

    def test_post_create(self):
        response = self.client.post('/api/post/', {
            'message': 'Test message',
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
