from datetime import datetime

from django import forms
from django.conf import settings
from django.db import models
from django.utils import simplejson as json
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from .widgets import ReCaptcha, captcha

__all__ = ['ReCaptchaField', 'JSONField']


class ReCaptchaField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': _(u'Invalid captcha')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptcha
        if not settings.DISABLE_CAPTCHA:
            self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        if settings.DISABLE_CAPTCHA:
            return False

        challenge = smart_unicode(values[0])
        response = smart_unicode(values[1])
        result = captcha.submit(
            challenge, response,
            settings.RECAPTCHA_PRIVATE_KEY, {}
        )
        if not result.is_valid:
            raise forms.util.ValidationError(
                self.error_messages['captcha_invalid']
            )

        return values[0]


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return super(JSONEncoder, self).default(self, obj)


class JSONField(models.TextField):
    encoder = JSONEncoder()

    def _dumps(self, data):
        return self.encoder.encode(data)

    def _loads(self, str):
        return json.loads(str, encoding=settings.DEFAULT_CHARSET)

    def db_type(self):
        return 'text'

    def save(self, model_instance):
        value = getattr(model_instance, self.attname, None)
        return self._dumps(value)

    def load(self, model_instance, json):
        setattr(model_instance, self.attname, self._loads(json))

    def pre_save(self, model_instance, add):
        return self.save(model_instance)

    def contribute_to_class(self, cls, name):
        self.class_name = cls
        super(JSONField, self).contribute_to_class(cls, name)
        models.signals.post_init.connect(self.post_init)
        setattr(cls, 'get_%s_json' % self.name, self.save)
        setattr(cls, 'set_%s_json' % self.name, self.load)

    def post_init(self, **kwargs):
        if ('sender' in kwargs
        and 'instance' in kwargs
        and kwargs['sender'] == self.class_name
        and hasattr(kwargs['instance'], self.attname)):
            value = self.value_from_object(kwargs['instance'])
            self.load(kwargs['instance'], value or 'null')
