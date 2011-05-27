# Chieftain by Paul Bagwell

## What?

Chieftain is a new generation imageboard (anonymous forum). It is the fastest chan.
It has plenty of modern features and modular design.
chieftain is built with HTML5, Python programming language, Django web framework,
Tornado scalable non-blocking web server with use of jQuery javascript library and
Memcached caching system.

## Features

* Lightweight architecture
* Realtime publish and subscribe system (post autoload)
* REST API with XML, YAML and JSON serializers
* Advanched post validation tools including tripcodes
* Markdown support with code highlighting
* Post search
* AJAX
* Answer maps & previews
* Bookmarks
* Customizable styles
* Advanced moderation and administration tools
* Internationalization (5 languages are supported currently)
* Mobile and smartphone versions
* Wakaba database converter

## Dependencies

* You need Python 2.7 to run chieftain.
* [Redis](http://redis.io/) or [Memcached](http://memcached.org/)
* [GeoIP C API](http://www.maxmind.com/app/c)
* [GeoIP datasets](http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/)
* All python dependencies are listed in the file pip-req.txt and can be
installed with command pip install -r pip-req.txt.

## Licensing

chieftain is licensed under MIT license. It means that you can copy, distribute,
adapt and transmit the work for free, but the copyright notice and license shall 
be included in all copies or substantial portions of chieftain.

Copyright (c) 2011 Paul Bagwell, http://chieftain.pbagwl.com/.

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