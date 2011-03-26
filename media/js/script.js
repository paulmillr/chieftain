/**
 * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 */

var queryString = parseQs(),
    answersMap = {},
    postButtons = {},
    votedPolls = new BoardStorage('polls'),
    workarounds = (function() {
        // pre-localize messages because of django bug
        gettext('Reason');
        gettext('Reply');
        gettext('Message is too long.');
        gettext('Full text');
        gettext('Thread');
        gettext('Post');
        gettext('hidden');
        gettext('bookmark');
        gettext('hide');
        gettext('Replies');
        gettext('New message in thread ');
        gettext('Post not found');

        // Recaptcha focus bug
        if (typeof Recaptcha !== 'undefined') {
            Recaptcha.focus_response_field = function() {};
        }

        if (!window.console) {
            window.console = {log: function() {}};
        }
    })(),
    // page detector
    curPage = (function() {
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

if(!Array.indexOf) {
	Array.prototype.indexOf = function(obj) {
		for(var i=0; i < this.length; i++) {
			if(this[i] == obj) {
				return i;
			}
		}
	}
}

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
    			var start = textarea.selectionStart,
    			    end = textarea.selectionEnd;
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
        var textarea = this.textarea,
            size = (tagStart + tagEnd).length;

        if (typeof textarea.selectionStart != "undefined") {
            var begin = textarea.value.substr(0, textarea.selectionStart),
                selection = textarea.value.substr(textarea.selectionStart, textarea.selectionEnd - textarea.selectionStart),
                end = textarea.value.substr(textarea.selectionEnd);
            textarea.selectionEnd = textarea.selectionEnd + size; 
            if (eachLine) {
                selection = selection.split('\n')
                selection = $.map(selection, function(x) {
                    return tagStart + x;
                }).join('\n')
                textarea.value = begin+selection+end;
            } else {
                textarea.value = begin+tagStart+selection+tagEnd+end;
            }
        }
        textarea.focus();
    }
});

function getThreadId(thread) {
    return thread.attr('id').replace('thread', '');
}

function getPostId(post) {
    return post.attr('data-id'); // it's faster than .data by ~10 times
}

function getPostPid(post) {
    if (isjQuery(post)) {
        return post.attr('id').replace('post', '');
    } else {
        return post.id.replace('post', '')
    }
    
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
 * Key-value database, based on localStorage
 *
 * Used for storing bookmarks, hidden posts and visited threads.
 */
function BoardStorage(storageName) {
    this.storageName = storageName;
}

$.extend(BoardStorage.prototype, {
    storageName: '',

    // gets all keys
    list: function() {
        var s = $.storage(this.storageName);
        return (typeof s !== 'undefined' && typeof s !== 'string' && s !== null) ? s : {};
    },

    get: function(key) {
        return this.list()[key]
    },

    set: function(key, value) {
        var l = this.list();
        l[key] = value;
        return $.storage(this.storageName, l);
    },

    incr: function(key, item) {
        var dict = this.get(key);
        if (typeof dict === 'object' && item in dict) {
            ++dict[item];
            this.set(key, dict);
            return dict[item];
        }
    },

    remove: function(key) {
        var s = this.list();
        delete s[key];
        return $.storage(this.storageName, s);
    },

    // Clears container.
    flush: function() {
        $.storage(this.storageName, '', 'flush');
    },

    sort: function(key) {
        var items = [],
            l = this.list();
        for (var i in l) {
            l[i]['id'] = i;
            items.push(l[i]);
        }
        items.sort(function(a, b) {
            if (key[0] == '-') {
                key = key.slice(1);
                return a[key] < b[key];
            } else {
                return a[key] > b[key];
            }
        });
        return items;
    }
});

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
    this.thread = (curPage.type === 'thread') ? curPage.cache.thread : this.span.closest('.thread');
    this.first = (curPage.type === 'thread') ? curPage.cache.first : this.thread.find('.post:first-child');
    this.id = getPostId(this.post);
    this.text_data = {
        'section': curPage.section,
        'first': getPostPid(this.first),
        'pid': getPostPid(this.post)
    };
}

/**
 * Simple color container class.
 * 
 * Used for storage of canvas data.
 */
function ColorContainer(red, green, blue, alpha) {
    if (!red) red = 0;
    if (!green) green = 0;
    if (!blue) blue = 0;
    if (!alpha) alpha = 1;
    this.data = [red, green, blue, alpha];
}

$.extend(ColorContainer.prototype, {
    data : [0, 0, 0, 1],
    red: function(v) {if (!v) return this.data[0]; else this.data[0] = v;},
    green: function(v) {if (!v) return this.data[1]; else this.data[1] = v;},
    blue: function(v) {if (!v) return this.data[2]; else this.data[2] = v;},
    alpha: function(v) {if (!v) return this.data[3]; else this.data[3] = v;},
    rgb: function() {return this.torgb(this.data);},
    rgba: function() {return this.torgba(this.data)},
    hex: function() {return this.tohex(this.data.slice(0,3))},
    hsl: function() {return this.tohsl(this.data.slice(0,3))},

    torgba: function(arr) {
        return 'rgba(' + arr.join(',') + ')';
    },

    torgb: function(arr) {
        return 'rgb(' + arr.slice(0,3).join(',') + ')';
    },

    tohex: function(arr) {
        function hex(number) {
            if (number instanceof Array) {
                var tmp = '';
                for (var i=0; i < number.length; i++) {
                    tmp += hex(number[i])
                }
                return tmp;
            }
            var char = '0123456789abcdef';
            if (number == null) {
                return '00';
            }
            number = parseInt(number);
            if (number == 0 || isNaN(number)) {
                return '00'
            }
            number = Math.round(Math.min(Math.max(0, number), 255));
            return char.charAt((number - number % 16) / 16) + char.charAt(number % 16);
        }
        return '#'+hex(arr);
    },

    tohsl: function(arr) {
        var r = arr[0], g = arr[1], b = arr[2];
        r /= 255, g /= 255, b /= 255;
        var max = Math.max(r, g, b), min = Math.min(r, g, b);
        var h, s, l = (max + min) / 2;

        if(max == min){
            h = s = 0; // achromatic
        }else{
            var d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch(max){
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }
            h /= 6;
        }

        return [Math.floor(h * 360), Math.floor(s * 100), Math.floor(l * 100)];
    }
});

function randomString(length) {
    function randomChar() {
        var n = Math.floor(Math.random() * 62);
        if (n < 10) {
            return n; //1-10
        } else if (n < 36) {
            return String.fromCharCode(n + 55); // A-Z
        } else {
            return String.fromCharCode(n + 61); // a-z
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
    var bodyHeight = $(window).height(),
        side = $('#sidebar'),
        sideHeight = side.height();

    if (sideHeight > bodyHeight) {
        side.height(parseInt(bodyHeight)).css('overflow-y', 'scroll');
    }
}

// Changes all labels to input placeholders.
function labelsToPlaceholders(list) {
    for (var i=0; i < list.length; i++) {
        var x = list[i],
            t = $('label[for="'+x+'"]').text(),
            dt = $('.' + x + '-d').find('dt').hide(),
            dd = $('#' + x);
        dd.attr('placeholder', t);
        dd.placeholder(t);
    }
}

// Manipulates elements. Used for user styles.
function manipulator(arr) {
    var cases = {
        after : function(from, to) {
            $(from).remove().insertAfter(to)
        },
        before : function(from, to) {
            $(from).remove().insertBefore(to);
        }
    };

    for (var i in arr) {
        for (var e=0; e < arr[i].length; e++) {
            cases[i](arr[i][e][0], arr[i][e][1])
        }
    }
}

// Query string parser.
function parseQs() {
    var d = location.href.split('?').pop().split('&'),
        parsed = {}, tmp;

    for (var i=0; i < d.length; i++) {
        var tmp = d[i].split('='); 
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

function showNewPostNotification(text, section, thread) {
    var nm = gettext('New message in thread '),
        title = nm + '/' + section + '/' + thread;
    if ($.dNotification.check()) {
        $.dNotification.show(text, 3000, title);
    }
}

function defaultErrorCallback(response) {
    //document.write(data.responseText); // for debugging
    var rt = response,
        errors,
        errorText,
        t = [], l;
    if (response['field-errors']) {
        errors = response['field-errors'];
        for (var i in errors) {
            // Get label text of current field
            l = $('label[for="'+i+'"]').text();
            t.push(l + ': ' + errors[i].join(', '));
        }
        errorText = t.join('<br/>')
    } else {
        errorText = rt['detail'];
    }

    $.notification('error', errorText);
}

function init() {
    var textArea = new PostArea('#message'),
        set = $.settings('hideSectGroup'),
        pass = $.localSettings('password'),
        buttons = {
            'bookmark': {storageName: 'Bookmarks'},
            'hide': {storageName: 'Hidden',
                onInit : function(data) {
                    if (data.span.hasClass('remove')) {
                        this.onAdd(data);
                    }
                },

                onAdd : function(data) {
                    var first = false,
                        post,
                        hideClass = 'hidden';
                    if (data.id === getPostId(data.first)) {
                        data.thread.addClass(hideClass);
                        post = data.first;
                        first = true;
                    } else {
                        post = data.post;
                    }
                    post.addClass(hideClass);
                    var t = first ? gettext('Thread') : gettext('Post'),
                        s = $('<span/>').addClass('skipped')
                        .text(t +
                            ' #'+ getPostPid(post) +
                            //'('+ post.find('.message').text().split(0, 20) +')' +
                            ' ' + gettext('hidden') + '.'
                        ).appendTo(post),
                        b = post.find('.bookmark, .hide').appendTo(s);
                },

                onRemove: function(data) {
                    var p;
                    if (data.id === getPostId(data.first)) {
                        data.thread.removeClass('hidden');
                        post = data.first;
                    } else {
                        post = data.post;
                    }
                    post.find('.bookmark, .hide').appendTo(post.find('header'));
                    post.find('.skipped').remove();
                    post.removeClass('hidden');
                }
            }
        }

    if (pass) {
        $('#password').val(pass);
    }

    $('#container').delegate('#password', 'change', function(event) {
        $.localSettings('password', this.value);
        $.settings('password', this.value);
    });

    function removeIfPreview(element) {
        element = isjQuery(element) ? element : $(element);
        element.remove();
        //console.log(element, element.parent())
    }

    for (var className in buttons) {
        var button = buttons[className],
            sname = button.storageName

        // Check if current button set is not blocked by user.
        if ($.settings('disable' + className)) {
            continue;
        }

        button.storage = new BoardStorage(sname);
        button.list = button.storage.list();

        window.postButtons[className] = button;
        $('.threads').addClass('with' + sname);
    }

    $('.bbcodes a').click(function(e) {
        e.preventDefault();
        var t = $(this),
            start = $(this).data('tag'),
            end = $(this).data('tagEnd'),
            code = t.attr('class') == 'code';
        if (end == undefined) {
            end = start;
        }

        textArea.wrap(start, end, code);
    });

    $('.threads').delegate('.post-icon', 'click', function(event) {
        event.preventDefault();
        var cont = new PostContainer(this),
            span = cont.span,
            post = cont.post,
            postId = cont.id,
            className = this.className.split(' ')[1],
            current = window.postButtons[className],
            storage = current.storage;

        if (span.hasClass('add')) {  // add
            span.removeClass('add').addClass('remove');
            storage.set(postId, cont.text_data);
            if (current.onAdd) {
                current.onAdd(cont);
            }
        } else {  // remove
            span.removeClass('remove').addClass('add');
            storage.remove(postId);
            if (current.onRemove) {
                current.onRemove(cont);
            }
        }
    });

    function previewPosts() {
        $('.threads').delegate('.postlink', 'mouseover', function(event) {
            var t = $(this),
                m = t.attr('href').match(/(?:\/(\w+)\/)?(\d+)/),
                globalLink = !!m[1] || !$('#post' + m[2]).length,
                board = m[1] || curPage.section,
                pid = m[2],
                post = t.closest('.post'),
                prevTree = post.hasClass('post-preview') ? post.parent() : false,
                timestamp = getCurrentTimestamp(),
                id = 'preview-' + pid + '-' + timestamp,
                top = event.clientY + (document.documentElement.scrollTop || document.body.scrollTop)
                left = event.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft + 1;

            if (globalLink) {
                //console.log('Searching the post', board, pid);
                var p = $('#post' + pid);
                if (p.length) {
                    return p;
                }

                $.get(window.api.url + '/post/' + board + '/' + pid + '?html=1')
                    .success(function(response) {
                        createPreview(response.html, board, pid, true, prevTree);
                    })
                    .error(function(xhr) {
                        $.notification('error', gettext('Post not found'));
                    });
            } else {
                createPreview($('#post' + pid).html(), board, pid, false, prevTree);
            }

            function createPreview(html, board, pid, globalLink, prevTree) {
                var to,
                    treeid = 'tree' + board + pid,
                    previews = $('<div class="post-previews-tree"/>').attr('id', treeid),
                    tree = $('#' + treeid),
                    div = $(html).clone(),
                    check = $(div.get(0)),
                    outer = $('<article/>').addClass('post post-preview')
                .attr('id', id)
                .css({'top': top + 11 +'px', 'left': left + 'px'});

                // remove icons
                div.find('.bookmark, .hide, .is_closed, .is_pinned').remove();
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
                var timeout,
                    prev = $('#' + id);
                link = link.add(prev);
                //console.log('Binded preview remove', prev);

                link.mouseout(function() {
                    timeout = window.setTimeout(function() {
                        //prev.remove();
                        removeIfPreview(prev);
                    }, 300);
                })
                .mouseover(function() {
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
        var t = $(this);
        t.next().toggle();
        $('.threads').toggleClass('deletingPosts');
    });

    $('#ban_ip').click(function(event) {
        var t = $(this),
            i = $('<input type="text" id="ban_reason" name="ban_reason"/>')
                .attr('placeholder', gettext('Reason'));
        if (t.attr('checked')) {
            i.insertAfter('label[for="ban_ip"]');
        } else {
            $('#ban_reason').remove();
        }
    });

    // Posts deletion
    $('.threads').delegate('.post', 'click', function(event) {
        if (!$('.threads').hasClass('deletingPosts')) {
            return true
        };
        var t = $(this),
            only_files = !!$('#only_files').attr('checked'),
            ban_ip = !!$('#ban_ip').attr('checked'),
            delete_all = !!$('#delete_all').attr('checked'),
            target = !only_files ? t : t.find('.file, .filemeta'),
            url = !only_files ? 
                window.api.url + '/post/' + target.data('id') : 
                window.api.url + '/file/' + getFileId(target.find('img')),
        password = $('#password').val();
        
        url += '?password=' + password;
        url += '&' + $('.removePosts').serialize();
        target.addClass('deleted');
        $.ajax({
            'url': url,
            'dataType': 'json',
            'type': 'DELETE'
        })
        .error(function(xhr) {
            $.notification('error', $.parseJSON(xhr.responseText)['detail']);
            target.removeClass('deleted');
        })
        .success(function(data) {
            if (only_files) {
                slideRemove(target);
                return true;
            }

            // Deleting all user posts.
            if (delete_all) {
                var t = target.find('.ip').text(),
                    d = $('.ip').filter(function() {
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

    $('.thread').delegate('.edit', 'click', function(event) {
        event.preventDefault();
        var c = new Canvas;
    });

    $('.threads').delegate('.number > a', 'click', function(e) {
        if (curPage.type === 'page' || curPage.type === 'thread') {
            if (!$.settings('disableFastReply')) {
                var n = $('#post' + $(this).text());
                $('.newpost').insertAfter(n);
                if (curPage.type === 'page') {
                    var thread_id = getThreadId(n.parent());
                    $('.newpost form').append('<input type="hidden" value="' + thread_id + '" id="thread" name="thread" />');
                    window.quickReplied = true;
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

    for (var i = 0; i < set.length; i++) {
        $('#list-group' + set[i]).slideToggle(0);
    }
}

function initSettings() {
    // those things depend on cookie settings
    var body = $('body'),
        qs = parseQs(),
        settings = $('.settings').find('input[type="checkbox"], select'),
        style = $('html').attr('id'),
        dn = $('#enableDesktopNotifications').click(function() {
            $.dNotification.request();
        });

    if (!$.dNotification.checkSupport() || $.dNotification.check()) {
        dn.closest('dl').hide();
    }

    $('#style').val(style);
    settings.each(function() {
        if (body.hasClass(this.id)) {
            this.checked = true;
        }
    });

    settings.change(function(event) {
        var value = this.value,
            id = this.id;
        if (this.checked !== undefined) {
            value = this.checked ? true : '';
        }
        $.settings(id, value);
    });

    $('#sidebar .hide').click(function(event) {
        event.preventDefault();
        var k = 'hideSidebar',
            h = $.settings(k) ? false : true;
        $.settings(k, h);
        changes[k](h);
    });

    $('#sidebar h3').click(function(e) {
        var num = this.id.split('group').pop(),
            key = 'hideSectGroup',
            set = $.localSettings(key),
            ul = $('#list-group' + num),
            hidden = (ul.css('display') == 'none');
        set = set ? set.split(',') : [];

        if (hidden && set.indexOf(num) !== -1) {
            set.splice(set.indexOf(num), 1);
        } else {
            set.push(num);
        }

        $.localSettings(key, set);
        ul.slideToggle(500, checkForSidebarScroll);
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

function initStyle() {
    var style = $.settings('style');

    checkForSidebarScroll();

    $('.tripcode:contains("!")').addClass('staff');
    
    $(document).scroll(function() {
        var pxo = window.pageXOffset,
            val = typeof pxo === 'number' ? pxo : document.body.scrollLeft;
        $('.sidebar').css('left', '-' + val + 'px');
    });

    if ($.settings('newForm')) {
        var styleInfo = {
                after : [
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
        var post = $(this),
            href = post.find('.number a').attr('href'),
            span = $('<span/>').addClass('answer')
                .html('[<a href="'+href+'">'+ gettext('Reply') +'</a>]');
        if (post.find('.is_closed').length == 0) {
            span.insertBefore(post.find('.number'));
        }
    });

    // Force english keys in captcha
    $('#main').delegate('#recaptcha_response_field', 'keypress', function(e) {
        var key;
        if (e.which < 1040 || e.which > 1279) {
            return true;
        }
        e.preventDefault();
        switch(e.which) {
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
        e.target.value = e.target.value + key;
    });

    // images resize
    $('.threads').delegate('.file', 'click', function(event) {
        event.preventDefault();
        var t = $(this),
            children = t.children(),
            p = t.closest('.post'),
            isResized = p.hasClass('resized');

        if (!isResized) {
            children.data('thumb', children.attr('src'));
            children.attr('src', $(this).attr('href'));
        } else {
            children.attr('src', children.data('thumb'));
        }
        p.toggleClass('resized');
    });

    $('.button').click(function() {
        $(this).toggleClass('active');
    })

    $('.expandImages').click(function(event) {
        event.preventDefault();
        $('.file').trigger('click');
    });

    $('.filterPosts .button').click(function() {
        var active = $(this).hasClass('active');
        $('.post').show();
        if (active) {
            var c = $('.filterPosts #filterImages');
            if (c.attr('checked')) {
                c.trigger('change');
            }
            $('.filterPosts .slider').trigger('slidechange');
        }
        $('.filterParams, .sliderInfo').toggle();
        $('.filterPosts .slider').toggle();
    });

    $('.filterPosts .slider').slider({
        'max': 15
    })
    .hide()
    .bind('slidechange', function() {
        var map = window.answersMap,
            posts = $('.post'),
            slider = $('.filterPosts .slider'),
            value = slider.slider('value'),
            replies;
        //console.log('Filtered posts with %s answers.', value);

        posts.filter(function() {
            var pid = getPostPid(this);
            if (value === 0) {
                return false;
            }

            // Hide posts, that don't have answers
            if (!(pid in map)) {
                return true;
            }

            // Hide posts with answers count less than value
            return map[pid].length < value;
        }).hide();
    });
    
    $('.filterPosts #filterImages').change(function() {
        var posts = $('.post').filter(function() {
            return !$(this).find('.file').length;
        }),
            checked = this.checked;
        if (checked) {
            posts.hide();
        } else {
            posts.show();
        }
    });

    $('.threads').delegate('.poll input[type="radio"]', 'click', function() {
        var radio = $(this);
        $.post(window.api.url + '/vote/', {'choice': this.value})
        .error(defaultErrorCallback)
        .success(function(data) {
            var total = 0,
                info = [],
                item,
                length,
                poll = radio.closest('dl'),
                pollId = parseInt(poll.attr('id').replace('poll', ''))
            
            for (var i=0; i < data.length; i++) {
                item = data[i];
                length = item.vote_count > 0 ? total / item.vote_count : 0;
                $('#vote-result' + item.id).text(item.vote_count);
            }

            $('.hbg-title').remove()
            window.votedPolls.set(pollId, radio.attr('value'));
            poll.horizontalBarGraph({interval: 0.1});
        });
    });

    // strip long posts at section page
    $('.post .message').each(function() {
        var t = $(this), parent, span, a;
        if (t.hasScrollBar()) {
            t.css('overflow', 'hidden');
            span = $('<span/>').addClass('skipped')
                .text(gettext('Message is too long.'))
                .appendTo(t.parent());
            a = $('<a/>').attr('href', '#showFullComment')
            .addClass('skipped')
            .text(gettext('Full text'))
            .click(function(event) {
                event.preventDefault();
                t.css('overflow', 'auto');
                $(this).parent().remove();
            })
            .appendTo(span);
        }
    });

    // modpanel
    $('.ip').each(function(x) {
        var t = $(this);
        t.insertBefore(t.prev().find('.number'));
    });

    if (!style) {
        return false;
    }

    $('html').attr('id', style);

    if (style === 'klipton') {
        function removeSel() {
            $('.postlist').remove();
            $('.selected').removeClass('selected');
            return false;
        }
        $('.thread').click(function(event) {
            if ($(this).hasClass('selected')) {
                removeSel();
                return false;
            }
            removeSel();
            $(this).addClass('selected');
            var s = $('<section/>').addClass('postlist').appendTo('#main'),
                p = $(this).find('.post').clone();
            p.appendTo(s)
            return false;
        });
    }

    return true;
}

function initPosts(selector) {
    var posts = selector && typeof selector !== 'function' ? 
            isjQuery(selector) ? selector : $(selector) : $('.post'),
        buttons = window.postButtons,
        map = {},
        cache = {};

    //if ($.browser.msie && $.browser.version === '7.0') {
    //    return true;
    //}

    for (var i=0; i < posts.length; i++) {
        var p = posts[i],
            post = $(p),
            id = getPostId(post),
            pid = getPostPid(post),
            links = post.find('.postlink').map(function() {return $(this);});

        // Initialize answers map.
        for (var j=0; j < links.length; j++) {
            var href = getPostLinkPid(links[j]),
                targetSelector = '#post' + href,
                target = $(targetSelector);

            if (href in map) {
                if (map[href].indexOf(pid) !== 0) {
                    map[href].push(pid);
                }
            } else {
                map[href] = [pid];
            }

            cache[href] = target

            if (curPage.type === 'thread' && target.length !== 0) {
                target.attr('href', targetSelector);
            }
        }

        // Initialize post buttons.
        /*for (var className in buttons) {
            var button = buttons[className],
                span = post.find('.' + className);

            if (id in button.list) {
                span.removeClass('add').addClass('remove');
            }

            if (button.onInit) {
                button.onInit(new PostContainer(span, post));
            }
        }*/
    }

    // Build or rebuild page answers map.
    for (var i in map) {
        var c = cache[i].find('.answer-map'),
            cacheExists = !!c.length,
            div = cacheExists ? c : $('<div class="answer-map"/>'),
            links = [],
            post = $('#post' + i),
            skipped = post.find('.skipped');
        for (var j=0; j < map[i].length; j++) {
            var text = map[i][j];
            links.push('<a class="postlink" href="#post'+ text +'">&gt;&gt;'+ text +'</a>');
        }

        if (!cacheExists) {
            div.html(gettext('Replies') + ':' + links.join(','));
        } else {
            div.html(div.html() + ',' + links.join(','));
        }
        
        if (skipped.length) {
            div.insertBefore(skipped);
        } else {
            post.append(div);
        }
        
        div.insertBefore( + '.skipped')
        $('#post' + i).append();
    }
    
    window.answersMap = map;
}

function initVisited() {
    if (!window.localStorage || $.settings('dontLogVisits')) {
        return true;
    }

    // Thread visits counter
    var storage = new BoardStorage('visitedThreads', true),
        visitedList = $('.' + storage.storageName);

    $('#dontLogVisits').click(function(event) {
        visitedList.slideToggle();
    });

    if (curPage.type === 'thread') {
        thread = curPage.thread;
        if (!(thread in storage.list())) {
            storage.set(thread, {
                'first': curPage.first, 
                'section': curPage.section,
                'visits': 1,
                'first_visit': (new Date()).getTime(),
                'title': $('.post:first-child .title').text(),
                'description': (function() {
                    var text = $('.post:first-child .message').text();
                    if (text.length > 100) {
                        text = text.substring(0, 100) + '...';
                    } 
                    return $.trim(text);
                })()
            })
        } else {
            storage.incr(thread, 'visits');
        }
    } else if (curPage.type == 'settings') {
        ul = visitedList.find('ul');
        visitedList.show();
        function makeList(list) {
            for (var i=0; i < list.length; ++i) {
                var a = $('<a/>'),
                    item = list[i],
                    elem = $('<li/>'),
                    tpl = '/' + item.section + '/' + item.first;
                a.attr('href', tpl);
                a.text(tpl + ': ' + item.description);
                ul.append(elem.append(a));
            }
        }
        makeList(storage.sort('visits'));
        $('.sortVisitedThreads').change(function(event) {
            ul.find('li').remove();
            makeList(storage.sort(this.value));
        });
        $('.clearVisitedThreads').click(function(event) {
            event.preventDefault();
            storage.flush();
            ul.children('li').slideUp('normal', function() {
                $(this).remove();
            });
        });
    }
}

function initHotkeys() {
    $('.newpost input, .newpost textarea').keydown('shift+return', function(event) {
        $('.newpost').submit();
        return false;
    });
}

function initAJAX() {
    if (!$('#password').val()) {
        $('#password').val(randomString(8));
    }

    function successCallback(data) {
        if (curPage.type !== 'thread' && !window.quickReplied) { // redirect
            window.location.href = './' + data.pid;
            return true;
        }

        if (window.quickReplied || $.settings('disablePubSub')) {
            //console.log('Received post html', data.html);
            var html = $(data.html);
                html = $([html[0], html[2]]),
                post = html.hide()
                .appendTo('#thread' + data.thread.id)
                .fadeIn(500);
            post.find('.tripcode:contains("!")').addClass('staff');
            initPosts(post);
        }

        if (window.quickReplied) {
            $('input[name="thread"]').remove();
            window.quickReplied = false;
        }

        var newpost = $('.newpost');
        if (newpost.parent().hasClass('thread')) {
            var b = $.settings('bottomForm') && curPage.type === 'thread' ? 
                '.actions' : '#main';
            newpost.insertBefore(b);
        }
        try {
            window.location.hash = '#post' + data.pid;
        } catch(e) {}
        $('.captcha-img').trigger('click');
        // clear entered data
        newpost.find(':input').each(function() {
            switch (this.type) {
                case 'email':
                case 'file':
                case 'select-multiple':
                case 'select-one':
                case 'text':
                case 'textarea':
                    $(this).val('');
                    break;
                case 'checkbox':
                case 'radio':
                    this.checked = false;
            }
        });
    }
    $('.newpost form').ajaxForm({
        //target: 'body',
        success: function(response) {
            //alert(response);
            if (typeof response === 'string') {
                response = $.parseJSON(response);
            }

            return !response['field-errors'] && !response['detail'] ? 
                successCallback(response) :
                defaultErrorCallback(response);
        },
        error: defaultErrorCallback,
        url: window.api.url + '/post/?html=1&_accept=text/plain',
        dataType: 'json'
    });
}

/**
 * Realtime publish-subscribe system.
 * 
 * Uses long polling to check for new posts.
 */
function initPubSub() {
    if (curPage.type !== 'thread' || $.settings('disablePubSub')) {
        return false;
    }
    var pubsub = {
        sleepTime: 500,
        maxSleepTime: 1000 * 60 * 15,
        cursor: null,

        poll: function() {
            var args = {};
            if (pubsub.cursor) {
                args.cursor = pubsub.cursor;
            }

            $.ajax(window.api.url + '/stream/'+ curPage.thread, {
                'type': 'POST',
                'dataType': 'json'
            })
            .error(function() {
                if (pubsub.sleepTime < pubsub.maxSleepTime) {
                    pubsub.sleepTime *= 2;
                } else {
                    pubsub.sleepTime = pubsub.maxSleepTime;
                }

                //console.log('Poll error; sleeping for', pubsub.sleepTime, 'ms');
                window.setTimeout(pubsub.poll, pubsub.sleepTime);
            })
            .success(function(response) {
                if (!response.posts) {
                    return false;
                }
                pubsub.cursor = response.cursor;
                var posts = response.posts,
                    text;

                pubsub.cursor = posts[posts.length - 1].id;
                //console.log(posts.length, 'new msgs');
                for (var i=0; i < posts.length; i++) {
                    var post = $(posts[i]).filter(function() {
                        // remove text nodes
                        var t = document.createTextNode('').__proto__;
                        //console.log('t', this.__proto__ != t)
                        return this.__proto__ != t;
                    })
                    .hide()
                    .appendTo('.thread')
                    .fadeIn(500, function() {
                        $(this).attr('style', '');
                    });

                    post.find('.tripcode:contains("!")').addClass('staff');
                    initPosts(post);
                }
                text = post.find('.message').text();
                showNewPostNotification(text, curPage.section, curPage.first);
                window.setTimeout(pubsub.poll, 0);
            });
        }
    }

    pubsub.poll();
}

$(function() {
    init();
    initSettings();
    initStyle();
    initPosts();
    initVisited();
    initHotkeys();
    initAJAX();
    initPubSub();
});
