#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Paul Bagwell on 2011-03-26.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from nose.tools import raises
from board.models import Post
from board.tools import make_post_descriptions, make_tripcode


def post_description_test():
    pass


def tripcode_test():
    assert make_tripcode('tripcode') == '3GqYIJ3Obs'
    assert make_tripcode('tripcod3') == 'U6qBEwdIxU'
    assert make_tripcode('##') == make_tripcode('###')


@raises(UnicodeEncodeError)
def invalid_tripcode_test():
    make_tripcode(u'тест')
