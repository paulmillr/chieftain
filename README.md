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
* Rename `settings_local_example.py` to `settings_local.py` and fill it with your database settings.
* 

## Contributing
* [Website](http://paulmillr.com/chieftain/)
* [Github](https://github.com/paulmillr/chieftain)

## Licensing
Chieftain is licensed under MIT license. It means that you can copy, distribute,
adapt and transmit the work for free, but the copyright notice and license shall
be included in all copies or substantial portions of chieftain. For more
details see LICENSE file.
