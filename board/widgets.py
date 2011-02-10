#!/usr/bin/env python
# encoding: utf-8
"""
widgets.py

Created by Paul Bagwell on 2011-02-07.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""

from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from recaptcha.client import captcha

__all__ = ['captcha', 'ReCaptcha']


class ReCaptcha(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe(u'{0}'.format(
            captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY)
        ))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None),
            data.get(self.recaptcha_response_name, None)]
