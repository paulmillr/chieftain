# encoding: utf-8
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
    text = '<p>hey <strong>guys</strong>, <b><i>how</i> are</b> you & me?</p>'
    stripped = 'hey **guys**, how are you & me?'
    eq_(models.strip_tags(text), stripped)


def parse_video_test():
    v = ('<object width="320" height="262"><param name="movie"'
    ' value="http://www.youtube.com/v/8Ampn-5hcZg"></param><param name="wmode"'
    ' value="transparent"></param><embed'
    ' src="http://www.youtube.com/v/8Ampn-5hcZg"'
    ' type="application/x-shockwave-flash" wmode="transparent" width="320"'
    ' height="262"></embed></object>')
    assert models.parse_video(v) == 'http://www.youtube.com/v/8Ampn-5hcZg'


def convert_test():
    pass
