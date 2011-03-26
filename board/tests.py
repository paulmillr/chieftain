#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Paul Bagwell on 2011-03-26.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from django.utils import unittest
from django.test.client import Client


class ModelsTest(unittest.TestCase):
    def setUp(self):
        # init test browser.
        self.client = Client()

    def test_post_create(self):
        
