# tire.js

This is a bunch of CSS things, images and jQuery plugins for fast development of web applications.

## Dependencies
jQuery 1.6.1

## License
This bundle is licensed under
the [http://www.opensource.org/licenses/mit-license.php](MIT license).

## CSS additions

- Awesome CSS3 button class (.button)

## jQuery plugins

- JS multipart uploader, which can upload files through ajax without iframe
- Plugin to work with REST APIs, which supports comet (long polling, websocket)
- Notifications (browser webkitnotifications are also supported)
- Cookies management
- HTML5 LocalStorage management

### Notifications

#### Usage
    $.notification('Notification text'[, type ('error', 'notice', 'warning', 'success')])

## Multipart uploader

Allows to easily upload images via AJAX without iframes. It uses HTML5
FileReader API to read binary data from files, so at the moment
it doesn't work in IE.

#### Usage
    var url = '/api/post/',
    var form = 'form.new-post',
    var mpu = $.mpu(url, form).error(function(xhr) {
      console.log('Error', xhr);
    }).success(function(data) {
      console.log('Success', data);
    });

## REST API plugin
Used to communicate with RESTful webapps.
Currently allowed methods are: GET, POST, PUT, DELETE.

Plugin also supports simple pubsub (like Socket.IO) with WebSockets
and long polling.

#### Usage
    $.api.url = '/api/2.0/';  // full path to the JSON api
    // you can also set API's content type with
    // $.api.dataType = 'xml';
    $.api.post('comment', {topic: 'Agreed', message: 'Totally agree'});

    // REST API basically is a wrapper around jQuery XHR objects, so you can
    // do with them anything you can do with jqxhr.
    $.api.get('comment/601').success(function(data) {
      var tpl = '<div class="comment">' + data.message + '</div>';
      $('#comments').append(tpl);
    });
    
    // DELETE http request
    $.api.del('comment/601').error(function() {
      console.log('Cannot delete comment');
    });

    // Long polling
    $.api.poll('feed').success(function(data) {
      $('#news').append('<div class="feed-item">' + data.info + '</div>');
    }).error(function() {
      // the default behavior of this callback is to restart poll
      // every t * 2 where t is time, passed since last error polling.
      console.log('Polling error!');
    });



