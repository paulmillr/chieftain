#!/usr/bin/env python
# encoding: utf-8
"""
tests.py

Created by Paul Bagwell on 2011-04-25.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from nose.tools import eq_, raises
from converter import models


def convert_ip_test():
    assert models.convert_ip(2231231116) == '132.253.226.140'
    assert models.convert_ip(1) == '0.0.0.1'


@raises(ValueError)
def invalid_convert_ip_test():
    models.convert_ip(-1)
    models.convert_ip(123213123123)


def strip_tags_test():
    text = '<p>hey <strong>guys</strong>, <b><i>how</i> are</b> you?</p>'
    stripped = 'hey **guys**, how are you?'
    eq_(models.strip_tags(text), stripped)


def convert_test():
    pass
