# Klipped

klipped - new generation imageboard.

## What?

klipped is a new generation imageboard. It is fastest open source chan.
It has plenty of modern features and modular design. klipped is built with
HTML5, Python programming language, Django web framework, Tornado scalable
non-blocking web server with use of jQuery javascript library and Memcached
memory caching system.

## Features

* Lightweight architecture
* Realtime publish and subscribe system (posts autoload)
* REST API with XML, YAML and JSON serializers
* Advanched post validation tools including tripcodes
* Markdown support with code highlighting
* Full-text search
* AJAX
* Answer maps & previews
* Customizable styles
* Advanced moderation and administration tools
* Internationalization (5 languages are supported currently)
* HTML5

### Planned for first release

* Mobile and smartphone versions
* HTML5 oekaki

## Dependencies

* [django](http://www.djangoproject.com/download/)
* [Tornado](http://www.tornadoweb.org/)
* [memcached](http://memcached.org/)
* [py-memcached](http://pypi.python.org/pypi/python-memcached/)
* [py-markdown2](https://github.com/pbagwl/markdown2)
* [ipcalc](http://pypi.python.org/pypi/ipcalc)
* [django-rest-framework](http://django-rest-framework.org/)
* [recaptcha-client](http://pypi.python.org/pypi/recaptcha-client)
* [PIL](http://www.pythonware.com/products/pil/)
* [GeoIP C API](http://www.maxmind.com/app/c)
* [GeoIP Python API](http://www.maxmind.com/app/python)
* [GeoIP datasets](http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/)
* Any supported by django SQL database binding (MySQLdb, postgresql, sqlite3,
Oracle)

## Licensing

Klipped is licensed under MIT license. It means that you can copy, distribute,
adapt and transmit the work for free, but the copyright notice and license shall 
be included in all copies or substantial portions of klipped.

Copyright (c) 2011 Paul Bagwell, http://klipped.pbagwl.com/.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.