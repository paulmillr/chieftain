# Chieftain
Chieftain is a new generation imageboard (anonymous forum). It is the fastest chan.
It has plenty of modern features and modular design.
Chieftain is built with HTML5, Python programming language, Django web framework,
Tornado scalable non-blocking web server with use of jQuery javascript library and
Memcached caching system.

## Features
* Lightweight architecture
* Realtime publish and subscribe system (post autoload)
* REST API with XML, YAML and JSON serializers
* Advanced post validation tools including tripcodes
* Markdown support with code highlighting
* Post search
* AJAX
* Answer maps & previews
* Bookmarks
* Customizable styles
* Advanced moderation and administration tools
* Internationalization
* Mobile and smartphone versions
* Wakaba database converter

## Dependencies
* You'll need Python 2.7 to run chieftain.
* [Redis](http://redis.io/) or [Memcached](http://memcached.org/)
* [GeoIP C API](http://www.maxmind.com/app/c): http://geolite.maxmind.com/download/geoip/api/c/GeoIP-1.4.8.tar.gz.
* (optional) [GeoIP datasets](http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/)
* All python dependencies are listed in the file pip-req.txt and can be
installed with command pip install -r pip-req.txt.

## Getting started
* Run `python manage.py syncdb` to fill database with base data.
* Run `python manage.py runserver` and `python pubsub.py`. It would start django & tornado webservers.
* You're done!

## Contributing
* [Website](http://paulmillr.com/chieftain/)
* [Github](https://github.com/paulmillr/chieftain)

## Licensing
The MIT License.

Copyright (c) 2011 Paul Miller

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
