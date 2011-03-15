#!/usr/bin/env python
# encoding: utf-8
"""
emitters.py

Created by Paul Bagwell on 2011-02-03.
Copyright (c) 2011 Paul Bagwell. All rights reserved.
"""
from djangorestframework.response import NoContent
from djangorestframework.emitters import *

try:
    import yaml
except ImportError:
    pass
else:
    class YAMLEmitter(BaseEmitter):
        """Emitter which serializes to YAML"""
        media_type = 'text/x-yaml'

        def emit(self, output=NoContent, verbose=False):
            if output is NoContent:
                return ''
            return yaml.safe_dump(output)


class JSONTextEmitter(JSONEmitter):
    """Emitter which serializes to JSON, but has media_type of plain text.
    
       Used because Firefox and Opera don't support application/json.
    """
    media_type = 'text/plain'
