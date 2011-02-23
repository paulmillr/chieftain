for (var i=0; i < 100; ++i) {
    $('#message').text('WIPE' + i);
    $.post('/api/post/', $('.new-post').serialize());
}