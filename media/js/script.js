/* Author: Paul Bagwell

*/
if (typeof Recaptcha !== 'undefined') {
    // workaround
    Recaptcha.focus_response_field = function() {};
}

var api = {
    url: '/api',
    defaultType: 'text/plain'    
},
    // pre-localize messages because of django bug
    i18n = (function() {
        var l = [
        gettext('Reason'),
        gettext('Reply'),
        gettext('Message is too long.'),
        gettext('Full text'),
        gettext('Thread'),
        gettext('Post'),
        gettext('hidden'),
        gettext('bookmark'),
        gettext('hide'),
    ];
    })(),
    // page detector
    currentPage = (function() {
    var loc = window.location.href.split('/').slice('3'),
        re = /(\d+)(?:.+)?/,
        data = {cache: {}};
    if (loc[1] == null) { // main, settings or faq
        l = loc[0];
        pages = ['settings', 'faq'];
        for (var i=0; i < pages.length; i++) {
            var c = pages[i]
            if (l.substr(0, c.length) === c) {
                data.type = c;
            }
        }
        data.type = data.type || 'main';
    } else { // section or thread
        data.section = loc[0];
        l = loc[1];
        if (l.match(/^\d+/)) {
            data.type = 'thread';
            data.cache.thread = $('.thread');
            data.thread = getThreadId(data.cache.thread);
            data.first = l.match(re)[1];
            data.cache.first = $('#post' + data.first);
        } else {
            if (l.match('posts')) {
                data.type = 'posts';
            } else if (l.match('threads')) {
                data.type = 'threads'
            } else {
                data.type = 'section';
            }
        }
    }
    
    return data;
})();

function PostArea(element) {
    // listens textarea and adds some methods to it

    this.textarea = $(element)[0];
    this.insert = function(text) {
    // inserts text in textarea and focuses on it
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
    }

    this.wrap = function(tagStart, tagEnd, eachLine) {
    // wraps selected text in tagStart text tagEnd
    // and inserts to textarea
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
}

function getThreadId(thread) {
    return thread.attr('id').replace('thread', '');
}

function getPostId(post) {
    return post.attr('data-id'); // it's faster than .data by ~10 times
}

function getPostPid(post) {
    return post.attr('id').replace('post', '');
}

function getPostLinkPid(postlink) {
    return postlink.href.replace(/(.*\/)?(\d+)/, '$2');
}

function BoardContainer(storageName) {
    // Key-value database, based on localStorage
    this.storageName = storageName;
}
$.extend(BoardContainer.prototype, {
    storageName : '',

    // gets all keys
    list: function() {
        var s = $.storage(this.storageName);
        return (typeof s !== 'undefined' && typeof s !== 'string' && s !== null) ? s : {};
    },

    // checks if key is in container
    // returns item if container is dictionary and 
    // bool(inList) if container is list
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
    
    // clears container
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
    },
});

function PostContainer(span, post) {
    if (!(span instanceof jQuery)) {
        span = $(span);
    }
    var isposts = (currentPage.type === 'posts');
    
    this.span = span;
    this.post = post ? (!(post instanceof jQuery) ? post : $(post)) : span.closest('.post');
    this.thread = (currentPage.type === 'thread') ? currentPage.cache.thread : this.span.closest('.thread');
    this.first = (currentPage.type === 'thread') ? currentPage.cache.first : this.thread.find('.post:first-child');
    this.id = getPostId(this.post);
    this.text_data = {
        'section': currentPage.section,
        'first': !isposts ? getPostPid(this.first) : '',
        'pid': getPostPid(this.post),
    };
}

/**
 * Simple color container class.
 * 
 * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 */
function ColorContainer(red, green, blue, alpha) {
    if (!red) red = 0;
    if (!green) green = 0;
    if (!blue) blue = 0;
    if (!alpha) alpha = 1;
    this.data = [red, green, blue, alpha];
}

ColorContainer.prototype = {
    data : [0, 0, 0, 1],
    get red() {return this.data[0]},
    get green() {return this.data[1]},
    get blue() {return this.data[2]},
    get alpha() {return this.data[3]},
    set red(value) {this.data[0] = value},
    set green(value) {this.data[1] = value},
    set blue(value) {this.data[2] = value},
    set alpha(value) {this.data[3] = value},

    get rgb() {
        return this.torgb(this.data)
    },
    get rgba() {
        return this.torgba(this.data)
    },
    get hex() {
        return this.tohex(this.data.slice(0,3))
    },
    get hsl() {
        return this.tohsl(this.data.slice(0,3))
    },
    
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
    },
}

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
        side = $('#sidebar aside'),
        sideHeight = side.height();

    if (sideHeight > bodyHeight) {
        side.height(parseInt(bodyHeight)).css('overflow-y', 'scroll');
    }
}

function labelsToPlaceholders(list) {
    for (var i=0; i < list.length; i++) {
        var x = list[i],
            t = $('label[for="'+x+'"]').text(),
            dt = $('.' + x + '-d').find('dt').hide(),
            dd = $('#' + x);
        dd.attr('placeholder', t);
        dd.placeholder(t);
    }
    //if ($('.bbcode').css('display') === 'none') {
    //    $('.captcha-d').css({'margin-top' : '1px'})
    //}
}

function manipulator(arr) {
    // manipulates elements. Used for user styles.
    var cases = {
        after : function(from, to) {
            $(from).remove().insertAfter(to)
        },
        before : function(from, to) {
            $(from).remove().insertBefore(to)
        },
    };
    
    for (var i in arr) {
        for (var e=0; e < arr[i].length; e++) {
            cases[i](arr[i][e][0], arr[i][e][1])
        }
    }
}


function styleDOM(style) {
    // make page changes, that can't be afforded through CSS
}

function parseQs(key) {
    // query string parser
    var d = location.href.split('?').pop().split('&'),
        parsed = {}, tmp;
        
    for (var i=0; i < d.length; i++) {
        var tmp = d[i].split('='); 
        parsed[tmp[0]] = tmp[1];
    }
    
    if (!key) {
        return parsed;
    }
    if (key in parsed) {
        return parsed[key];
    }
    return false;
}

function slideRemove(elem) {
    if (typeof elem !== 'object') {
        elem = $(elem);
    }
    elem.slideUp(600, function() {
        $(this).remove();
    });
}

function init() {
    var textArea = new PostArea('#message'),
        set = $.settings('hideSectGroup'),
        pass = $.settings('password');
    if (pass) {
        $('#password').val(pass);
    }
    $('#main').delegate('#password', 'change', function(event) {
        $.settings('password', this.value);
    });

    function searchPost(board, pid, callback) {
        var p = $('#post' + pid);
        if (p.length) {
            return p;
        }
        $.get(window.api.url + '/post/' + board + '/' + pid, function(data) {
            callback(data.html);
        });
    }
    
    function removeIfPreview(element) {
        element = element instanceof jQuery ? element : $(element);
        var p = element.prev();
        if (p.hasClass('post-preview')) {
            removeIfPreview(p);
            p.remove();
        }
        element.remove();
    }

    $('.bbcode a').click(function(e) {
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
    
    $('.thread').delegate('.postlink', 'clicka', function(event) {
        event.preventDefault();
        window.location.hash = '#' + $(this).attr('href');
    });
    
    function buildAnswersMap() {
        var map = {};
        $('.postlink').each(function() {
            var pid = parseInt(getPostPid($(this).closest('.post'))),
                href = getPostLinkPid(this);
            if (map[href]) {
                map[href].push(pid);
            } else {
                map[href] = [pid];
            }
        });

        for (var i in map) {
            var div = $('<div class="answer-map"/>'),
                links = [];
            for (var j=0; j < map[i].length; j++) {
                var text = map[i][j];
                    links.push('<a class="postlink"  href="#post'+text+'">&gt;&gt;'+text+'</a>');
            }
            div.html(gettext('Replies') + ':' + links.join(','));
            $('#post' + i + ' .post-wrapper').append(div);
        }
    }
    
    function previewPosts() {
        $('.postlink').each(function(x) {
            var pid = getPostLinkPid(this);
            if ($('#post' + pid).length === 0) {
                return true;
            }
            this.href = '#post' + pid;
        });
        
        $('.threads').delegate('.postlink', 'mouseover', function(event) {
            event.preventDefault();
            var t = $(this),
                m = t.attr('href').match(/(?:\/(\w+)\/)?(\d+)/),
                globalLink = !!m[1],
                board = globalLink ? m[1] : currentPage.section,
                pid = m[2],
                post = t.closest('.post'),
                timestamp = getCurrentTimestamp(),
                id = 'preview-' + pid + '-' + timestamp,
                top = event.clientY + (document.documentElement.scrollTop || document.body.scrollTop)
                left = event.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft + 1;
                function callback(html) {
                    var div = $(html).clone(),
                        outer = $('<article/>').addClass('post post-preview')
                    .attr('id', id)
                    .css({'top': top + 11 +'px', 'left': left + 'px'})
                    .hover(function(ev) {}, function(ev) {
                        if ($(ev.target).hasClass('post-preview')) {
                            return false;
                        }
                        removeIfPreview(this);
                    });

                    window.mouseOnPreview = true;

                    // remove icons
                    div.find('.bookmark, .hide, .is_closed, .is_pinned').remove();
                    outer.append(div).insertAfter(post);
                }
                if (globalLink) {
                    searchPost(board, pid, callback);
                } else {
                    callback($('#post' + pid).html());
                }

                t.bind('mouseout', function(ev) {
                    if (!$(ev.target).is('.post-preview')) {
                        return false;
                    }
                    $('#' + id).remove();
                });
        });
    }
    
    if (!$.settings('disablePostsPreview')) {
        previewPosts();
    }
    if (!$.settings('disableAnswersMap')) {
        buildAnswersMap();
    }
    
    $('.deleteMode > input').click(function(event) {
        var tmp = this.value,
            t = $(this),
            fn;
        this.value = t.data('back');
        t.data('back', tmp);
        t.next().toggle();
        if (!$('.ip').length) {
            $('.modPanel').remove();
        }
        if (t.attr('class') == 'toggled') {
            t.removeClass('toggled');
            t.addClass('toggle');
            $('.deleted').removeClass('deleted');
        } else {
            t.removeClass('toggle');
            t.addClass('toggled');
        }
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
    $('#main').delegate('.post', 'click', function(event) {
        if ($('.deleteMode input').attr('class') !== 'toggled') {
            return true;
        }
        var t = $(this),
            only_files = !!$('#only_files').attr('checked'),
            ban_ip = !!$('#ban_ip').attr('checked'),
            delete_all = !!$('#delete_all').attr('checked'),
            target = !only_files ? t : t.find('.files'),
            url = !only_files ? 
                window.api.url + '/post/' + target.data('id') : 
                window.api.url + '/file/' + target.find('.file').attr('id').replace(/file/, ''),
            password = $('#password').val();

        url += '?password=' + password;
        url += '&' + $('.deleteMode').serialize();
        target.addClass('deleted');
        $.ajax({
            'url': url,
            'type': 'DELETE',
        })
        .error(function(data) {
            $.message('error', $.parseJSON(data.responseText)['detail']);
            target.removeClass('deleted');
        })
        .success(function(data) {
            if (only_files) {
                slideRemove(t.find('.files, .file-info'));
                return true;
            }
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
            if (target.prev().length !== 0) {
                // post is not first in thread
                slideRemove(target);
                return true;
            }

            // remove whole thread
            if (currentPage.type === 'thread') {
                window.location.href = './';
                return true;
            }
            var thread = target.parent();
            thread.children().addClass('deleted');
            slideRemove(thread);
        });
    });
    
    $('#main > .thread').delegate('.edit', 'click', function(event) {
        event.preventDefault();
        var c = new Canvas;
    });
    
    $('.threads').delegate('.number > a', 'click', function(e) {
        if (!$.settings('oldInsert') && currentPage.type != 'section') {
            var n = $('#post' + $(this).text());
            $('.new-post').insertAfter(n);
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
    var s = parseQs(), 
        settings = $('.settings').find('select, input'),
        changes = { // description of all functions on settings pages
            ustyle: function(x) {
                if (x !== 'ustyle') {
                    $('html').attr('id',  x);
                }
            },
            
            toggleNsfw: function(x) {
                if (x) {
                    $('.post img').addClass('nsfw');
                } else {
                    $('.post img').removeClass('nsfw');
                }
            },
            
            hideSidebar: function(x) {
                $('#container-wrap').toggleClass('no-sidebar');
                $('#sidebar').toggle(0, null);
            },

            hideNav: function(x) {
                $('nav').toggle();
            },

            hideSectBanner: function(x) {
                $('.section-banner').toggle();
            },
            
            newForm: function(x) {
                if (!x) {
                    return false;
                }
                
                var styleInfo = {
                    after : [
                        ['.new-post input[type="submit"]', '.captcha'],
                        ['.password-d', '.topic-d'],
                        ['.file-d', '.password-d'],
                    ],
                };

                labelsToPlaceholders(['username', 'email', 'topic', 'message', 'captcha']);
                $('.new-post').addClass('new-style')
                $('.empty').remove();
                manipulator(styleInfo);
            },
            
            hideBBCodes: function(x) {
                $('.bbcode').hide();
            },
        };
        
    for (var x in s) {
        $.settings(x, s[x]);
    }
    
    settings.each(function(x) {
        var s = $.settings(this.id), 
            t = parseQs(this.id);
        if (!!t) {
            $.settings(this.id, t);
            s = t;
        }
        if (s !== null) {
            if (s === 'false') {
                s = false;
            }
            
            if (this.checked == null) {
                this.value = s;
            } else {
                this.checked = s;
            }
        }
    });
    
    
    settings.change(function(event) {
        var value = this.value;
        if (this.checked !== undefined) {
            value = this.checked ? true : '';
        }
        console.log('Setting %s changed to "%s".', this.id, value);
        $.settings(this.id, value);
    });
    
    $('#sidebar .hide').click(function(event) {
        var k = 'hideSidebar',
            h = $.settings(k) ? false : true;
        $.settings(k, h);
        changes[k](h);
    });
    
    $('#sidebar h4').click(function(e) {
        var num = this.id.split('group').pop(),
            key = 'hideSectGroup',
            set = $.settings(key),
            ul = $('#list-group' + num),
            hidden = (ul.css('display') == 'none');
        set = set ? set.split(',') : [];
        
        if (hidden && set.indexOf(num) !== -1) {
            set.splice(set.indexOf(num), 1);
        } else {
            set.push(num);
        }
        
        $.settings(key, set);
        ul.slideToggle(500, checkForSidebarScroll);
    });
    
    $('.threads').delegate('.nsfw', 'hover', function(event) {
        $(this).toggleClass('nsfw');
    });
    
    $('.toggleNsfw').click(function(event) {
        event.preventDefault();
        var k = 'toggleNsfw',
            c = $.settings(k),
            v = c ? '' : 1;
        $.settings(k, v);
        changes.toggleNsfw(v);
    });
    
    for (var id in changes) {
        var func = changes[id],
            c = $.settings(id);
        if (c) {
            func(id);
        }
    }
}

function initStyle() {
    var key = 'ustyle',
        style = $.settings(key);
    
    checkForSidebarScroll();

    $('.tripcode:contains("!")').addClass('staff');

    document.onscroll = function() {
        $('.sidebar').css('left', '-' + document.body.scrollLeft + 'px')
    };
    
    $('.section .post:first-child').each(function(x) {
        var post = $(this),
            href = post.find('.number a').attr('href'),
            span = $('<span/>').addClass('answer')
                .html('[<a href="'+href+'">'+ gettext('Reply') +'</a>]');
        if (post.find('.is_closed').length == 0) {
            span.insertBefore(post.find('.number'));
        }
    });
    
    // images resize
    $('.threads').delegate('.post:not(.resized) .files a', 'click', function(event) {
        event.preventDefault();
        var children = $(this).children();
        children.data('thumb', children.attr('src'));
        children.attr('src', $(this).attr('href'));
        $(this).closest('.post').addClass('resized');
    });
    
    $('.threads').delegate('.post.resized .files a', 'click', function(event) {
        event.preventDefault();
        var children = $(this).children();
        $(this).closest('.post').removeClass('resized');
        children.attr('src', children.data('thumb'));
    });

    // strip long posts at section page
    $('.section .post .content').each(function() {
        var t = $(this), parent, span, a;
        if (t.hasScrollBar()) {
            t.addClass('overflow-hidden');
            span = $('<span/>').addClass('skipped')
                .text(gettext('Message is too long.'))
                .appendTo(t.parent());
            a = $('<a/>').attr('href', '#showFullComment')
            .addClass('skipped')
            .text(gettext('Full text'))
            .click(function(event) {
                event.preventDefault();
                t.removeClass('overflow-hidden');
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

function initHidden() {
    var status = ('localStorage' in window && window['localStorage'] !== null);
    if (!status) {
        return false;
    }
    
    if (!$.settings('dontLogVisits')) {
        initVisitedThreads();
    }
    
    // Thread visits counter
    function initVisitedThreads() {
        var container = new BoardContainer('visitedThreads', true),
            visitedList = $('.' + container.storageName);

        $('#dontLogVisits').click(function(event) {
            visitedList.slideToggle();
        });

        if (currentPage.type == 'thread') {
            thread = currentPage.thread;
            if (!(thread in container.list())) {
                container.set(thread, {
                    'first': currentPage.first, 
                    'section': currentPage.section,
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
                container.incr(thread, 'visits');
            }
        } else if (currentPage.type == 'settings') {
            ul = visitedList.find('ul');
            visitedList.show();
            function makeList(list) {
                for (var i=0; i < list.length; ++i) {
                    var a = $('<a/>'),
                        item = list[i],
                        elem = $('<li/>'),
                    // elem.data('visits', item.visits);
                        tpl = '/'+item.section+'/'+item.first;
                    a.attr('href', tpl);
                    a.text(tpl + ': ' + item.description);
                    ul.append(elem.append(a));
                }
            }
            makeList(container.sort('visits'));
            $('.sortVisitedThreads').change(function(event) {
                ul.find('li').remove();
                makeList(container.sort(this.value));
            });
            $('.clearVisitedThreads').click(function(event) {
                event.preventDefault();
                container.flush();
                ul.children('li').slideUp('normal', function() {
                    $(this).remove();
                });
            });
        }
    }
}

function initButtons(selector) {
    var status = ('localStorage' in window && window['localStorage'] !== null),
        selector = typeof selector == 'function' ? $('.post') : selector;
    if (!status) {
        return false;
    }
    function buttonInitializer(data) {
        var dataCopy = {};
        $.each(data, function() {
            var item = this;
            dataCopy[this.className] = this;

            if (!!$.settings('disable' + item.container)) {
                return true;
            }
            
            dataCopy[item.className] = item;

            var container = new BoardContainer(item.container),
                list = container.list(),
                className = item.className;

            selector.each(function(x) {
                var span = $('<span/>').attr('title', gettext(className))
                    .addClass(className).addClass('add'),
                    post = $(this);

                if (getPostId(post) in list) {
                    span.removeClass('add').addClass('remove');
                }
                span.appendTo(post.find('header'));
                if (!!item.onInit) {
                    item.onInit(new PostContainer(span, post));
                }
            });
            
            if (window.buttonsInitialized) {
                return true;
            }

            $('.threads').delegate('.' + className, 'click', function(event) {
                event.preventDefault();
                var post = new PostContainer(this),
                    span = post.span,
                    className = this.className.split(' ')[0],
                    dt = dataCopy[className];
                if (span.hasClass('add')) {  // add
                    span.removeClass('add').addClass('remove');
                    container.set(post.id, post.text_data);
                    if (dt.onAdd) {
                        dt.onAdd(post);
                    }
                } else {  // remove
                    span.removeClass('remove').addClass('add');
                    container.remove(post.id);
                    if (dt.onRemove) {
                       dt.onRemove(post);
                    }
                }
            });
        });
    }
    
    buttonInitializer([
        {
            container: 'Bookmarks', 
            className: 'bookmark'
        },
        {
            container: 'Hidden', 
            className: 'hide',
            onInit : function(data) {
                if (data.span.hasClass('remove')) {
                    this.onAdd(data);
                }
            },

            onAdd : function(data) {
                var first = false, post;
                if (data.id === getPostId(data.first)) {
                    data.thread.addClass('hidden')
                    post = data.first;
                    first = true;
                } else {
                    post = data.post;
                }
                post.addClass('hidden')
                var t = first ? gettext('Thread') : gettext('Post'),
                    s = $('<span/>').addClass('skipped')
                    .text(t +
                        ' #'+ getPostPid(post) +
                        //'('+ post.find('.message').text().split(0, 20) +')' +
                        ' ' + gettext('hidden') + '.'
                    ).appendTo(post.find('.post-wrapper')),
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
    ]);
    if (!window.buttonsInitialized) {
        window.buttonsInitialized = true;
    }
}

function initHotkeys() {
    $('.new-post input, .new-post textarea').keydown('shift+return', function(event) {
        $('.new-post').submit();
        return false;
    });
}

function initAJAX() {
    if (!$('#password').val()) {
        $('#password').val(randomString(8));
    }
    if ($.settings('noAJAX')) {
        return true;
    }
    function errorCallback(data) {
        //document.write(data.responseText); // for debugging
        var rt = data,
            errors,
            errorText,
            t = [], l;
        if (rt['field-errors']) {
            errors = rt['field-errors'];
            for (var i in errors) {
                // Get label text of current field
                l = $('label[for="'+i+'"]').text();
                t.push(l + ': ' + errors[i].join(', '));
            }
            errorText = t.join('<br/>')
        } else {
            errorText = rt['detail'];
        }

        $.message('error', errorText);
    }

    function successCallback(data) {
        if (currentPage.type === 'section') { // redirect
            window.location.href = './' + data.pid;
            return true;
        }
        if ($.settings('disablePubSub')) {
            var post = $(data.html).hide()
                .appendTo('.thread')
                .fadeIn(500);
            post.find('.tripcode:contains("!")').addClass('staff');
            initButtons(post);
        }

        var newpost = $('.new-post');
        if (newpost.parent().attr('id') !== 'main') {
            newpost.insertBefore('.threads');
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
    $('.new-post').ajaxForm({ 
        target: 'body',
        success: function(data) {
            return !data['field-errors'] && !data['detail'] ? 
                successCallback(data) :
                errorCallback(data);
        },
        url: window.api.url + '/post/?_accept=text/plain',
        dataType: 'json',
    });
}

function initPubSub() {
    if (currentPage.type !== 'thread' || $.settings('disablePubSub')) {
        return false;
    }
    var pubsub = {
        sleepTime: 500,
        cursor: null,

        poll: function() {
            var args = {};
            if (pubsub.cursor) {
                args.cursor = pubsub.cursor;
            }
            
            $.ajax('/api/stream/'+ currentPage.thread +'/subscribe', {
                type: 'POST',
                dataType: 'text',
            })
            .error(function() {
                pubsub.sleepTime *= 2;
                if (pubsub.sleepTime > 60000) {
                    pubsub.sleepTime = 4000;
                }
                
                console.log('Poll error; sleeping for', pubsub.sleepTime, 'ms');
                window.setTimeout(pubsub.poll, pubsub.sleepTime);
            })
            .success(function(response) {
                try {
                    response = $.parseJSON(response);
                } catch(e) {}
                if (!response.posts) {
                    return false;
                }
                pubsub.cursor = response.cursor;
                var posts = response.posts;
                pubsub.cursor = posts[posts.length - 1].id;
                //console.log(posts.length, 'new msgs', pubsub.cursor);

                for (var i=0; i < posts.length; i++) {
                    var post = $(posts[i]).hide()
                        .appendTo('.thread')
                        .fadeIn(500);
                        post.find('.tripcode:contains("!")').addClass('staff');
                        initButtons(post);
                }
                window.setTimeout(pubsub.poll, 0);
            });
        },
    }

    pubsub.poll();
}


$(init);
$(initSettings);
$(initStyle);
$(initHidden);
$(initButtons);
$(initHotkeys);
$(initAJAX);
$(initPubSub);