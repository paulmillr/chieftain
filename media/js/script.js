/**
 * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 */
(function(window, $, undefined) {
"use strict";

var app = {};

$.extend({
  settings: function(name, value) {
    var elem = $('body');
    if (typeof name === 'undefined') {
      return elem.attr('class').split(' ');
    } else if (typeof value === 'undefined') {
      if (name === 'style') {
        return $('html').attr('id');
      } else {
        return elem.hasClass(name);
      }
    } else {
      if (name === 'style') {
        $('html').attr('id', value)
      } else {
        elem.toggleClass(name)
      }
      switch (name) {
        case 'style':
          $('html').attr('id', value);
          break;
        default:
          elem.toggleClass(name);
          break;
      }
      var type = 'post';
      var url = 'setting/';
      var data = {'key': name, 'value': value};

      if (value === 'false' || value === false || value === '') {
        value = '';
        type = 'del';
        url += data.key;
      }
      type = type.toLowerCase();
      $.api[type](url, data).error(function(xhr) {
        $.notification('error', gettext('Settings error'));
      });
    }
  }
});

$.fn.hasScrollBar = function() {
  return this.get(0).scrollHeight - 1 > this.height();
};

// pre-localize messages because of django bug
var m = [
  'Reason', 'Reply', 'Message is too long.', 'Full text', 'Thread',
  'Post', 'hidden', 'hide', 'Replies', 'New message in thread ', 'Post not found'
];
for (var i = 0, l = m.length; i < l; i++) {
  gettext(m[i]);
}

// Recaptcha focus bug
if (typeof Recaptcha !== 'undefined') {
  Recaptcha.focus_response_field = function() {};
}

var curPage = (function() {
  // page detector
  var data = {
    type: $('#container').attr('role'),
    cache: {}
  };

  switch (data.type) {
    case 'page':
    case 'posts':
    case 'threads':
      data.section = window.location.href.split('/')[3];
      break;
    case 'thread':
      data.section = window.location.href.split('/')[3];
      data.type = 'thread';
      data.cache.thread = $('.thread');
      data.cache.first = $('.post:first');
      data.thread = getThreadId(data.cache.thread);
      data.first = getPostPid(data.cache.first);
      break;
    default:
      break;
  }

  return data;
})();

function isjQuery(object) {
  return object instanceof jQuery;
}

/**
 * Tools for textareas.
 */
function PostArea(element) {
  this.textarea = $(element)[0];
}

$.extend(PostArea.prototype, {
  // inserts text in textarea and focuses on it
  insert: function(text) {
    var textarea = this.textarea;
  	if (textarea) {
  		if (textarea.createTextRange && textarea.caretPos) { // IE
  			var caretPos = textarea.caretPos;
  			if (caretPos.text.charAt(caretPos.text.length-1) == ' ') {
  			  caretPost.text = text + ' ';
  			} else {
  			  caretPos.text = text;
  			}
  		} else if (textarea.setSelectionRange) { // Firefox
  			var start = textarea.selectionStart;
  			var end = textarea.selectionEnd;
  			textarea.value = textarea.value.substr(0, start) + text + textarea.value.substr(end);
  			textarea.setSelectionRange(start + text.length, start + text.length);
  		} else {
  			textarea.value += text + " ";
  		}
  		textarea.focus();
  	}
  },

  // wraps selected text in tagStart text tagEnd
  // and inserts to textarea
  wrap: function(tagStart, tagEnd, eachLine) {
    var textarea = this.textarea;
    var size = (tagStart + tagEnd).length;

    if (typeof textarea.selectionStart != "undefined") {
      var v = textarea.value;
      var begin = v.substr(0, textarea.selectionStart);
      var selection = v.substr(textarea.selectionStart, textarea.selectionEnd - textarea.selectionStart);
      var end = v.substr(textarea.selectionEnd);
      textarea.selectionEnd = textarea.selectionEnd + size;
      if (eachLine) {
        selection = selection.split('\n');
        selection = $.map(selection, function(x) {
          return tagStart + x;
        }).join('\n');
        textarea.value = begin + selection + end;
      } else {
        textarea.value = begin + tagStart + selection + tagEnd + end;
      }
    }
    textarea.focus();
  }
});

function getThreadId(thread) {
  return parseInt(thread.attr('data-id'), 10);
}

function getPostId(post) {
  return parseInt(post.attr('data-id'), 10);
}

function getPostPid(post) {
  return parseInt(isjQuery(post) ? post.attr('data-pid') : post['data-pid'], 10);
}

function getPostLinkPid(postlink) {
  return postlink.text().match(/>>(\/\w+\/)?(\d+)/)[2];
}

function getPostNumberPid(postnumber) {
  return postnumber.text();
}

function getFileId(file) {
  return file.attr('id').replace('file', '');
}

/**
 * Post container class.
 *
 * Used to push post data in various 'button-click' events.
 */
function PostContainer(span, post) {
  if (!isjQuery(span)) {
    span = $(span);
  }
  var isposts = (curPage.type === 'posts');

  this.span = span;
  this.post = post ? (!isjQuery(post) ? post : $(post)) : span.closest('.post');
  if (curPage.type === 'thread') {
    this.thread = curPage.cache.thread;
    this.first = curPage.cache.first;
  } else {
    this.thread = this.span.closest('.thread');
    this.first = this.thread.find('.post:first-child');;
  }
  this.id = getPostId(this.post);
  this.text_data = {
    'section': curPage.section,
    'first': getPostPid(this.first),
    'pid': getPostPid(this.post)
  };
}

function randomString(length) {
  function randomChar() {
    var n = Math.floor(Math.random() * 62);
    if (n < 10) {
      return n; //1-10
    } else if (n < 36) {
      return String.fromCharCode(n + 55);  // A-Z
    } else {
      return String.fromCharCode(n + 61);  // a-z
    }
  }
  var s = '';
  while(s.length < length) {
    s += randomChar();
  }
  return s;
}

function getCurrentTimestamp() {
  return (new Date()).getTime().toString().slice(0, 10);
}

function checkForSidebarScroll() {
  var bodyHeight = $(window).height();
  var side = $('#sidebar');
  var sideHeight = side.height();

  if (sideHeight > bodyHeight) {
    side.height(parseInt(bodyHeight, 10)).css('overflow-y', 'scroll');
  }
}

// Changes all labels to input placeholders.
function labelsToPlaceholders(list) {
  for (var i=0; i < list.length; i++) {
    var x = list[i];
    var t = $('label[for="' + x + '"]').text();
    var dt = $('.' + x + '-d').find('dt').hide();
    var dd = $('#' + x);
    dd.attr('placeholder', t);
    dd.placeholder(t);
  }
}

// Manipulates elements. Used for user styles.
function manipulator(arr) {
  var cases = {
    after: function(from, to) {
      $(from).remove().insertAfter(to)
    },
    before: function(from, to) {
      $(from).remove().insertBefore(to);
    }
  };

  for (var i in arr) {
    for (var e = 0, l = arr[i].length; e < l; e++) {
      cases[i](arr[i][e][0], arr[i][e][1])
    }
  }
}

// Query string parser.
function parseQs() {
  var d = location.href.split('?').pop().split('&');
  var parsed = {};
  var tmp;

  for (var i = 0, l = d.length; i < l; i++) {
    tmp = d[i].split('=');
    parsed[tmp[0]] = tmp[1];
  }

  return parsed;
}

function slideRemove(elem) {
  if (typeof elem !== 'object') {
    elem = $(elem);
  }
  elem.slideUp(600, function() {
    $(this).remove();
  });
}

function defaultErrorCallback(response) {
  //document.write(data.responseText); // for debugging 
  var errors = response['field-errors'] || response['detail'];
  var errorText = '';
  var tmp = [];
  var text, label;
  //console.log('Response', response, ', errors', errors);
  if (typeof errors === 'string') {
    errorText = errors;
  } else {
    for (var i in errors) {
      text = '';
      label = $('label[for="' + i + '"]');
      if (label.length) {
        text += label.text() + ': ';
      }
      text += errors[i].join(', ');
      tmp.push(text)
    }
    errorText = tmp.join('<br/>');
  }

  $.notification('error', errorText);
}

$.extend(app, {
board: {
  queryString: parseQs(),
  postButtons: {},

  init: function() {
    var textArea = new PostArea('#message');
    var set = $.settings('hideSectGroup');
    var pass = $.cookie('password');
    var buttons = {
      feed: {storeText: true},
      hidden: {
        onInit: function(data) {
          if (data.span.hasClass('remove')) {
            this.onAdd(data);
          }
        },

        onAdd: function(data) {
          var first = false;
          var post;
          var hideClass = 'hidden';
          if (data.id === getPostId(data.first)) {
            data.thread.addClass(hideClass);
            post = data.first;
            first = true;
          } else {
            post = data.post;
          }
          post.addClass(hideClass);
          var t = first ? gettext('Thread') : gettext('Post');
          var s = $('<span/>').addClass('hide-msg').text(
            t + ' #'+ getPostPid(post) +
            ' ' + gettext('hidden') + '.'
          ).appendTo(post);
          var b = post.find('.post-icon').appendTo(s);
        },

        onRemove: function(data) {
          var p;
          if (data.id === getPostId(data.first)) {
            data.thread.removeClass('hidden');
            post = data.first;
          } else {
            post = data.post;
          }
          post.find('.post-icon').appendTo(post.find('header'));
          post.find('.hide-msg').remove();
          post.removeClass('hidden');
        }
      }
    };

    if (pass) {
      $('#password').val(pass);
    }

    $('#container').delegate('#password', 'change', function(event) {
      $.cookie('password', this.value);
      $.settings('password', this.value);
    });

    function removeIfPreview(element) {
      element = isjQuery(element) ? element : $(element);
      element.remove();
      //console.log(element, element.parent())
    }

    for (var storageName in buttons) {
      var button = buttons[storageName];

      // Check if current button set is not blocked by user.
      if ($.settings('disable' + storageName)) {
        continue;
      }

      app.board.postButtons[storageName] = button;
      $('.threads').addClass('with' + storageName);
    }

    $('.bbcodes a').click(function(e) {
      e.preventDefault();
      var $this = $(this);
      var start = $this.data('tag');
      var end = $this.data('tagEnd');
      var isCode = $this.attr('class') === 'code';
      if (typeof end === 'undefined') {
        end = start;
      }

      textArea.wrap(start, end, isCode);
    });

    // TODO: Toggleclass
    $('.threads').delegate('.post-icon', 'click', function(event) {
      event.preventDefault();
      var t = $(this);
      var cont = new PostContainer(t, t.closest('.post'));
      var span = cont.span;
      var post = cont.post;
      var postId = cont.id;
      var storageName = t.attr('data-storage');
      var current = app.board.postButtons[storageName];
      var apiLink = storageName + '/';

      if (span.hasClass('add')) {  // add
        span.removeClass('add').addClass('remove');
        $.api.post(apiLink, {value: postId}).error(defaultErrorCallback);
        if (current.onAdd) {
          current.onAdd(cont);
        }
      } else {  // remove
        span.removeClass('remove').addClass('add');
        $.api.del(apiLink + postId).error(defaultErrorCallback);
        if (current.onRemove) {
          current.onRemove(cont);
        }
      }
    });

    $('#container[role="storage"]').delegate('.post-icon', 'click', function() {
      event.preventDefault();
      var t = $(this);
      var postId = getPostId(t.closest('tr'));
      var storageName = t.attr('data-storage');
      var apiLink = storageName + '/';
      if (t.hasClass('add')) {
        t.removeClass('add').addClass('remove');
        $.api.post(apiLink, {value: postId}).error(defaultErrorCallback);
      } else {
        t.removeClass('remove').addClass('add');
        $.api.del(apiLink + postId).error(defaultErrorCallback);
      }
    });

    $('.storage-clear-icon').click(function(event) {
      $.api.del($(this).attr('data-storage'));
    });

    function previewPosts() {
      $('.threads').delegate('.postlink', 'mouseover', function(event) {
        var $this = $(this);
        var m = $this.attr('href').match(/(?:\/(\w+)\/)?(\d+)/);
        var globalLink = !!m[1] || !$('#post' + m[2]).length;
        var board = m[1] || curPage.section;
        var pid = m[2];
        var post = $this.closest('.post');
        var prevTree = post.hasClass('post-preview') ? post.parent() : false;
        var timestamp = getCurrentTimestamp();
        var id = 'preview-' + pid + '-' + timestamp;
        var doc = document.documentElement;
        var body = document.body;
        var top = event.clientY + (doc.scrollTop || body.scrollTop);
        var left = event.clientX + (doc.scrollLeft || body.scrollLeft) - doc.clientLeft + 1;

        if (globalLink) {
          //console.log('Searching the post', board, pid);
          var p = $('.post[data-pid="' + pid + '"]');
          if (p.length) {
            return p;
          }

          var url = 'post/' + board + '/' + pid + '?html=1';
          $.api.get(url).success(function(response) {
            createPreview(response.html, board, pid, true, prevTree);
          }).error(function(xhr) {
            $.notification('error', gettext('Post not found'));
          });
        } else {
          createPreview($('#post' + pid).html(), board, pid, false, prevTree);
        }

        function createPreview(html, board, pid, globalLink, prevTree) {
          var treeid = 'tree' + board + pid;
          var previews = $('<div class="post-previews-tree"/>').attr('id', treeid);
          var tree = $('#' + treeid);
          var div = $(html).clone();
          var check = $(div.get(0));
          var outer = $('<article/>').addClass('post post-preview')
            .attr('id', id)
            .css({'top': top + 11 +'px', 'left': left + 'px'});
          var to;

          // remove icons
          div.find('.post-icon, .is_closed, .is_pinned').remove();
          // we've got post information through API, so
          // remove not necessary elements
          if (check.hasClass('post')) {
            //console.log('Global link', check);
            div = check.children();
          }

          if (globalLink) {
            div.find('.number a').attr('href', '/' + board + '/' + pid);
          }

          if (!$('#' + outer.attr('id')).length) {
            outer.append(div);
            if (prevTree) {
              outer.appendTo(prevTree);
            } else {
              previews.appendTo('.threads').append(outer);
            }
          }
        }

        function bindRemovePreview(link, id) {
          var prev = $('#' + id);
          var timeout;
          link = link.add(prev);
          //console.log('Binded preview remove', prev);

          link.mouseout(function() {
            timeout = window.setTimeout(function() {
              //prev.remove();
              removeIfPreview(prev);
            }, 300);
          }).mouseover(function() {
            window.clearTimeout(timeout);
          });
        }

        window.setTimeout(function() {
          bindRemovePreview(t, id);
        }, 200);
      });
    }

    if (!$.settings('disablePostsPreview')) {
      previewPosts();
    }

    $('.actions .removePosts .button').click(function(event) {
      event.preventDefault();
      var $this = $(this);
      $this.next().toggle();
      $('.threads').toggleClass('deletingPosts');
    });

    $('#ban_ip').click(function(event) {
      var $this = $(this);
      var $input = $('<input type="text" id="ban_reason" name="ban_reason"/>')
        .attr('placeholder', gettext('Reason'));

      if ($this.attr('checked')) {
        $input.insertAfter('label[for="ban_ip"]');
      } else {
        $('#ban_reason').remove();
      }
    });

    // Posts deletion
    $('.threads').delegate('.post', 'click', function(event) {
      if (!$('.threads').hasClass('deletingPosts')) {
        return true
      };
      var $this = $(this);
      var onlyFiles = !!$('#only_files').attr('checked');
      var banIp = !!$('#ban_ip').attr('checked');
      var deleteAll = !!$('#delete_all').attr('checked');
      var target = !onlyFiles ? $this : $this.find('.file, .filemeta');
      var url = !onlyFiles ?
          'post/' + target.data('id') :
          'file/' + getFileId(target.find('img'));
      password = $('#password').val();

      url += '?password=' + password;
      url += '&' + $('.removePosts').serialize();
      target.addClass('deleted');
      $.api.del(url).error(function(xhr) {
        $.notification('error', $.parseJSON(xhr.responseText)['detail']);
        target.removeClass('deleted');
      }).success(function(data) {
        if (onlyFiles) {
          slideRemove(target);
          return true;
        }
        // Deleting all user posts.
        if (deleteAll) {
          var t = target.find('.ip').text();
          $('.ip').filter(function() {
            return $(this).text() === t;
          }).each(function() {
            var post = $(this).closest('.post');
            post.addClass('deleted');
            slideRemove(post);
          });
        }

        // post is not first in thread
        if (target.prev().length !== 0) {
          slideRemove(target.add(target.find('img')));
        } else {
          if (curPage.type === 'thread') {
            window.location.href = './';
          }
          var thread = target.parent();
          thread.children().addClass('deleted');
          slideRemove(thread);
        }
      });
    });

    $('.threads').delegate('.number > a', 'click', function(e) {
      if (curPage.type === 'page' || curPage.type === 'thread') {
        if (!$.settings('disableQuickReply')) {
          var n = $('#post' + $(this).text());
          $('.newpost').insertAfter(n);
          if (curPage.type === 'page') {
            var thread_id = getThreadId(n.parent());
            var input = '<input type="hidden" value="' + thread_id + '" id="thread" name="thread" />';
            $('.newpost form').append(input);
            ajax.quickReplied = true;
          }
        }
        textArea.insert('>>' + e.target.innerHTML + ' ');
        return false
      } else {
        return true;
      }
    });

    // sidebar-related
    if (!set) {
      return false;
    }
    set = set.split(',');

    for (var i = 0, l = set.length; i < l; i++) {
      $('#list-group' + set[i]).slideToggle(0);
    }
  }
},

settings: {
  init: function() {
    // those things depend on cookie settings
    var body = $('body');
    var qs = parseQs();
    var settings = $('#container[role="settings"]')
      .find('input[type="checkbox"], select');
    var style = $('html').attr('id');
    var dn = $('#enableDesktopNotifications').click(function() {
      $.notification.request();
    });

    if (!$.notification.checkSupport() || $.notification.check()) {
      dn.closest('dl').hide();
    }

    $('#style').val(style);

    settings.each(function() {
      var $this = $(this);
      if (body.hasClass($this.attr('id'))) {
        $this.attr('checked', true);
      }
    });

    settings.change(function(event) {
      var $this = $(this);
      var value = $this.val();
      var id = $this.attr('id');
      if ($this.attr('checked') !== undefined) {
        value = $this.attr('checked') ? true : '';
      }
      $.settings(id, value);
    });

    $('#sidebar .hide').click(function(event) {
      event.preventDefault();
      var key = 'hideSidebar';
      var value = !$.settings(k);
      $.settings(key, value);
      changes[key](value);
    });

    $('#sidebar h3').click(function(e) {
      var $this = $(this);
      var num = $this.attr('id').split('group').pop();
      var key = 'hideSectGroup';
      var set = $.cookie(key);
      var $ul = $('#list-group' + num);
      var hidden = (ul.css('display') === 'none');
      set = set ? set.split(',') : [];

      if (hidden) {
        var iof = set.indexOf(num);
        if (iof !== -1) {
          set.splice(iof, 1);
        }
      } else {
        set.push(num);
      }

      $.cookie(key, set);
      $ul.slideToggle(500, checkForSidebarScroll);
    });

    $('.toggleNsfw').click(function(event) {
      event.preventDefault();
      var bool = $('body').hasClass('nsfw') ? '' : true;
      $.settings('nsfw', bool);
    });

    $('.nsfw .threads').delegate('img', 'hover', function(event) {
      $(this).toggleClass('nsfw');
    });
  }
},

style: {
  init: function() {
    var style = $.settings('style');
    checkForSidebarScroll();
    $('.tripcode:contains("!")').addClass('staff');

    $(document).scroll(function() {
      var pxo = window.pageXOffset;
      var val = typeof pxo === 'number' ? pxo : document.body.scrollLeft;
      $('.sidebar').css('left', '-' + val + 'px');
    });

    if ($.settings('newForm')) {
      var styleInfo = {
        after: [
          ['.newpost input[type="submit"]', '.file-d'],
          ['.password-d', '.topic-d'],
          ['.file-d', '.message-d'],
        ]
      };

      labelsToPlaceholders(['username', 'email', 'topic', 'message', 'captcha']);
      $('.newpost').addClass('new-style')
      $('.empty').remove();
      manipulator(styleInfo);
    }

    $('.section .post:first-child').each(function(x) {
      var $this = $this;
      var href = $this.find('.number a').attr('href');
      var span = $('<span/>').addClass('answer')
        .html('[<a href="'+href+'">'+ gettext('Reply') +'</a>]');
      if ($this.find('.is_closed').length == 0) {
        span.insertBefore($this.find('.number'));
      }
    });

    // Force english keys in captcha
    $('#main').delegate('#recaptcha_response_field', 'keypress', function(event) {
      var key;
      if (event.which < 1040 || event.which > 1279) {
        return true;
      }
      event.preventDefault();
      switch(event.which) {
        case 1081: key = 'q'; break;
        case 1094: key = 'w'; break;
        case 1091: key = 'e'; break;
        case 1082: key = 'r'; break;
        case 1077: key = 't'; break;
        case 1085: key = 'y'; break;
        case 1075: key = 'u'; break;
        case 1096: key = 'i'; break;
        case 1097: key = 'o'; break;
        case 1079: key = 'p'; break;
        case 1092: key = 'a'; break;
        case 1099: key = 's'; break;
        case 1074: key = 'd'; break;
        case 1072: key = 'f'; break;
        case 1087: key = 'g'; break;
        case 1088: key = 'h'; break;
        case 1086: key = 'j'; break;
        case 1083: key = 'k'; break;
        case 1076: key = 'l'; break;
        case 1103: key = 'z'; break;
        case 1095: key = 'x'; break;
        case 1089: key = 'c'; break;
        case 1084: key = 'v'; break;
        case 1080: key = 'b'; break;
        case 1090: key = 'n'; break;
        case 1100: key = 'm'; break;
        default: return true;
      }
      event.target.value = event.target.value + key;
    });

    // images resize
    $('.threads').delegate('.file', 'click', function(event) {
      event.preventDefault();
      var $this = $(this);
      var $children = $this.children();
      var $post = $this.closest('.post');
      var isResized = $post.hasClass('resized');

      if (!isResized) {
        $children.data('thumb', children.attr('src'));
        $children.attr('src', $this.attr('href'));
      } else {
        $children.attr('src', children.data('thumb'));
      }
      $post.toggleClass('resized');
      $post.parent().toggleClass('resized');
    });

    $('.button').click(function(event) {
      $(this).toggleClass('active');
    });

    $('.expandImages').click(function(event) {
      event.preventDefault();
      $('.file').trigger('click');
    });

    $('.filterPosts .button').click(function(event) {
      var active = $(this).hasClass('active');
      $('.post').show();
      if (active) {
        var $checkbox = $('.filterPosts #filterImages');
        if ($checkbox.attr('checked')) {
          $checkbox.trigger('change');
        }
        $('.filterPosts .slider').trigger('slidechange');
      }
      $('.filterParams, .sliderInfo').toggle();
      $('.filterPosts .slider').toggle();
    });

    $('.filterPosts .slider')
      .slider({max: 15})
      .hide()
      .bind('slidechange', function() {
        var $posts = $('.post');
        var $slider = $('.filterPosts .slider');
        var value = slider.slider('value');
        var $filtered = posts.filter(function() {
          var pid = getPostPid(this);
          if (value === 0) {
            $posts.show();
            return false;
          }
          // Hide posts, that don't have answers
          if (!(pid in app.posts.map)) {
            return true;
          }

          // Hide posts with answers count less than value
          return app.posts.map[pid].length < value;
        });
        console.log(app.posts.map);
        console.log('Filtered posts with %s answers.', value);
        console.log($filtered);
        $filtered.hide();
    });

    $('.filterPosts #filterImages').change(function() {
      var posts = $('.post').filter(function() {
        return !$(this).find('.file').length;
      });
      var checked = this.checked;
      if (checked) {
        posts.hide();
      } else {
        posts.show();
      }
    });

    // strip long posts at section page
    $('.post .message').each(function() {
      var $this = $(this);
      if ($this.hasScrollBar()) {
        $this.css('overflow', 'hidden');
        var span = $('<span/>').addClass('skipped')
          .text(gettext('Message is too long.'))
          .appendTo($this.parent());
        var a = $('<a href="#showFullComment" class="skipped"/>')
          .text(gettext('Full text'))
          .click(function(event) {
            event.preventDefault();
            $this.css('overflow', 'auto');
            $(this).parent().remove();
          })
          .appendTo(span);
      }
    });

    // modpanel
    $('.ip').each(function(x) {
      var $this = $(this);
      $this.insertBefore($this.prev().find('.number'));
    });

    if (!style) {
      return false;
    }

    $('html').attr('id', style);

    if (style === 'klipton') {
      $('.thread').click(function(event) {
        var $this = $(this);
        $('.postlist').remove();
        $('.selected').removeClass('selected');
        if ($this.hasClass('selected')) {
          return false;
        }
        $this.addClass('selected');
        var $section = $('<section/>').addClass('postlist').appendTo('#main');
        var $post = $(this).find('.post').clone();
        $post.appendTo($section)
        return false;
      });
    }

    $('.kTabs').tabs();
  }
},

posts: {
  map: {},
  data: {},
  cache: {},

  init: function(selector) {
    var posts = selector && typeof selector !== 'function' ?
      isjQuery(selector) ?
        selector :
        $(selector) :
      $('.post');
    var map = {};
    this.cache = {};

    for (var i = 0, l = posts.length; i < l; i++) {
      var post = posts[i];
      var $post = $(post);
      var $links = $post.find('.postlink').map(function() {
        return $(this);
      });
      var pid = getPostPid($post);

      // Initialize answers map.
      for (var j = 0, ll = links.length; j < ll; j++) {
        var href = getPostLinkPid(links[j]);
        var targetSelector = '#post' + href;
        var $target = $(targetSelector);

        if (href in map) {
          if (map[href].indexOf(pid) !== 0) {
            map[href].push(pid);
          }
        } else {
          map[href] = [pid];
        }

        this.cache[href] = $target

        if (curPage.type === 'thread' && $target.length !== 0) {
          $target.attr('href', targetSelector);
        }
      }
    }

    this.initButtons();
    this.buildAnswersMap(map, true);
  },

  initButtons: function() {
    var $posts = $('.thread .post:first-child');
    var buttons = app.board.postButtons;

    $posts.each(function() {
      var post = $(this);
      var id = getPostId(post);

      for (var storageName in buttons) {
        var button = buttons[storageName];
        var $span = post.find('.post-icon[data-storage="' + storageName + '"]');
        var idInStorage = window.session[storageName].indexOf(id);

        if (idInStorage !== null && idInStorage >= 0) {
          $span.removeClass('add').addClass('remove');
        }

        if (button.onInit) {
          button.onInit(new PostContainer($span, post));
        }
      }
    });
  },

  buildAnswersMap: function(map, concat) {
    if ($.settings('disableAnswersMap')) {
      return false;
    }
    for (var i in map) {
      var links = [];
      var $cache = this.cache[i].find('.answer-map');
      var cacheExists = !!$cache.length;
      var $div = cacheExists ?
        $cache :
        $('<div class="answer-map"/>');
      var $post = $('#post' + i);
      var $skipped = $post.find('.skipped');

      for (var j = 0, ll = map[i].length; j < ll; j++) {
        var text = map[i][j];
        links.push('<a class="postlink" href="#post'+ text +'">&gt;&gt;'+ text +'</a>');
      }

      if (!cacheExists) {
        $div.html(gettext('Replies') + ':' + links.join(','));
      } else {
        $div.html($div.html() + ',' + links.join(','));
      }

      if (skipped.length) {
        $div.insertBefore(skipped);
      } else {
        $post.append(div);
      }

      $div.insertBefore( + '.skipped');
      $('#post' + i).append();
    }

    if (concat) {
      for (var attr in map) {
        this.map[attr] = map[attr];
      }
    }
  }
},

hotkeys: {
  init: function() {
    // TODO.
  }
},

ajax: {
  validCaptchas: 0,
  quickReplied: false,

  init: function() {
    var $password = $('#password');
    if (!$password.val()) {
      $password.val(randomString(8));
    }

    $('.newpost form').ajaxForm({
      //target: 'body',
      success: function(response) {
        //alert(response);
        if (typeof response === 'string') {
          response = $.parseJSON(response);
        }

        if (response['field-errors'] || response['errors'] || response['detail']) {
          defaultErrorCallback(response);
        } else {
          ajax.success(response)
        }
      },
      error: defaultErrorCallback,
      url: $.api.url + 'post/?html=1',
      dataType: 'json'
    });
  },

  success: function(data) {
    //console.log(data);
    if (curPage.type !== 'thread' && !ajax.quickReplied) { // redirect
      window.location.href = './' + data.pid;
      return true;
    }

    if (ajax.quickReplied || $.settings('disablePubSub')) {
      //console.log('Received post html', data.html);
      var $html = $(data.html);
      var $html = $([$html[0], $html[2]]);
      var $post = $html
        .hide()
        .appendTo('#thread' + data.thread.id)
        .fadeIn(500);
      $post.find('.tripcode:contains("!")').addClass('staff');
      initPosts($post);
    }

    if (ajax.quickReplied) {
      $('input[name="thread"]').remove();
      ajax.quickReplied = false;
    }

    if (++this.validCaptchas > 2) {
      $('.captcha-d').remove();
    }

    var newpost = $('.newpost');
    if (newpost.parent().hasClass('thread')) {
      var b = $.settings('bottomForm') && curPage.type === 'thread' ?
        '.actions' :
        '#main';
      newpost.insertBefore(b);
    }
    try {
      window.location.hash = '#post' + data.pid;
    } catch(e) {}
    $('.captcha-img').trigger('click');
    // clear entered data
    newpost.find(':input').each(function() {
      var $this = $(this);
      switch ($this.attr('type')) {
        case 'email':
        case 'file':
        case 'select-multiple':
        case 'select-one':
        case 'text':
        case 'textarea':
          $this.val('');
          break;
        case 'checkbox':
        case 'radio':
          $this.attr('checked', false);
          break;
      }
    });
  }
},

/**
 * Realtime publish-subscribe system.
 *
 * Uses long polling to check for new posts.
 */
pubsub: {
  sleepTime: 500,
  maxSleepTime: 1000 * 60 * 15,
  cursor: null,
  newMsgs: 0,

  init: function() {
    if (curPage.type !== 'thread' || $.settings('disablePubSub')) {
      return false;
    }

    this.poll();
  },

  showNewPostNotification: function(text, section, thread) {
    var pageTitle = $('title').text().split('] ').pop();
    var dnTitle = gettext('New message in thread ') + '/' + section + '/' + thread;

    // increment new messages count
    $('title').text('[' + (++this.newMsgs) + '] ' + pageTitle);

    // add new messages counter to the window title
    $(document).mousemove(function(event) {
      $('title').text(pageTitle);
      $(document).unbind('mousemove');
      app.pubsub.newMsgs = 0;
    });

    if ($.notification.check()) {
      $.notification.show(text, 3000, dnTitle);
    }
  },

  poll: function() {
    var args = {};
    if (app.pubsub.cursor) {
      args.cursor = app.pubsub.cursor;
    }
    $.api.post('stream/'+ curPage.thread).error(function() {
      if (app.pubsub.sleepTime < app.pubsub.maxSleepTime) {
        app.pubsub.sleepTime *= 2;
      } else {
        app.pubsub.sleepTime = app.pubsub.maxSleepTime;
      }

      //console.log('Poll error; sleeping for', pubsub.sleepTime, 'ms');
      window.setTimeout(app.pubsub.poll, app.pubsub.sleepTime);
    }).success(function(response) {
      if (!response.posts) {
        return false;
      }
      app.pubsub.cursor = response.cursor;
      var posts = response.posts;

      app.pubsub.cursor = posts[posts.length - 1].id;
      //console.log(posts.length, 'new msgs');
      for (var i = 0, l = posts.length; i < l; i++) {
        var $p = $(posts[i]);
        var $post = $([$p[0], $p[2]])  // p[1] is text node
          .hide()
          .appendTo('.thread')
          .fadeIn(500, function(event) {
            $(this).attr('style', '');
        });

        $post.find('.tripcode:contains("!")').addClass('staff');
        app.posts.init($post);
      }
      var text = $post.find('.message').text();
      app.pubsub.showNewPostNotification(text, curPage.section, curPage.first);
      window.setTimeout(app.pubsub.poll, 0);
    });
  }
}
});

$(function() {
  var l = ['board', 'settings', 'style', 'posts', 'hotkeys', 'ajax', 'pubsub'];
  $.each(l, function(i, item) {
    app[item].init();
  });
});

window.app = app;

})(window, jQuery);