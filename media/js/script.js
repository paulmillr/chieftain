/* Author: Paul Bagwell

*/

var currentPage = (function() { // page detector
    var pageType,
        loc = window.location.href.split('/').slice('3'),
        re = /(\d+)(?:.+)?/,
        l, section, thread, op_post;
    if (loc[1] == null) { // main, settings or faq
        l = loc[0];
        pages = ['settings', 'faq'];
        for (var i=0; i < pages.length; i++) {
            var c = pages[i]
            if (l.substr(0, c.length) === c) {
                pageType = c;
            }
        }
        pageType = pageType || 'main';
    } else { // section or thread
        section = loc[0];
        l = loc[1];
        if (l.match(/^\d+/)) {
            pageType = 'thread';
            thread = $('.thread').attr('id').match(re)[1];
            op_post = l.match(re)[1];
        } else {
            pageType = 'section';
        }
    }
    
    return {
        'type' : pageType,
        'section' : section,
        'thread' : thread,
        'op_post' : op_post,
    }
})();

/*
 * Crypto-JS v2.0.0
 * SHA256
 * http://code.google.com/p/crypto-js/
 * Copyright (c) 2009, Jeff Mott. All rights reserved.
 * http://code.google.com/p/crypto-js/wiki/License
 */
(function(){var c="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";var d=window.Crypto={};var a=d.util={rotl:function(h,g){return(h<<g)|(h>>>(32-g))},rotr:function(h,g){return(h<<(32-g))|(h>>>g)},endian:function(h){if(h.constructor==Number){return a.rotl(h,8)&16711935|a.rotl(h,24)&4278255360}for(var g=0;g<h.length;g++){h[g]=a.endian(h[g])}return h},randomBytes:function(h){for(var g=[];h>0;h--){g.push(Math.floor(Math.random()*256))}return g},bytesToWords:function(h){for(var k=[],j=0,g=0;j<h.length;j++,g+=8){k[g>>>5]|=h[j]<<(24-g%32)}return k},wordsToBytes:function(i){for(var h=[],g=0;g<i.length*32;g+=8){h.push((i[g>>>5]>>>(24-g%32))&255)}return h},bytesToHex:function(g){for(var j=[],h=0;h<g.length;h++){j.push((g[h]>>>4).toString(16));j.push((g[h]&15).toString(16))}return j.join("")},hexToBytes:function(h){for(var g=[],i=0;i<h.length;i+=2){g.push(parseInt(h.substr(i,2),16))}return g},bytesToBase64:function(h){if(typeof btoa=="function"){return btoa(e.bytesToString(h))}for(var g=[],l=0;l<h.length;l+=3){var m=(h[l]<<16)|(h[l+1]<<8)|h[l+2];for(var k=0;k<4;k++){if(l*8+k*6<=h.length*8){g.push(c.charAt((m>>>6*(3-k))&63))}else{g.push("=")}}}return g.join("")},base64ToBytes:function(h){if(typeof atob=="function"){return e.stringToBytes(atob(h))}h=h.replace(/[^A-Z0-9+\/]/ig,"");for(var g=[],j=0,k=0;j<h.length;k=++j%4){if(k==0){continue}g.push(((c.indexOf(h.charAt(j-1))&(Math.pow(2,-2*k+8)-1))<<(k*2))|(c.indexOf(h.charAt(j))>>>(6-k*2)))}return g}};d.mode={};var b=d.charenc={};var f=b.UTF8={stringToBytes:function(g){return e.stringToBytes(unescape(encodeURIComponent(g)))},bytesToString:function(g){return decodeURIComponent(escape(e.bytesToString(g)))}};var e=b.Binary={stringToBytes:function(j){for(var g=[],h=0;h<j.length;h++){g.push(j.charCodeAt(h))}return g},bytesToString:function(g){for(var j=[],h=0;h<g.length;h++){j.push(String.fromCharCode(g[h]))}return j.join("")}}})();
(function(){var g=Crypto,b=g.util,c=g.charenc,f=c.UTF8,e=c.Binary;var a=[1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298];var d=g.SHA256=function(j,h){var i=b.wordsToBytes(d._sha256(j));return h&&h.asBytes?i:h&&h.asString?e.bytesToString(i):b.bytesToHex(i)};d._sha256=function(q){if(q.constructor==String){q=f.stringToBytes(q)}var y=b.bytesToWords(q),z=q.length*8,r=[1779033703,3144134277,1013904242,2773480762,1359893119,2600822924,528734635,1541459225],s=[],K,J,I,G,F,E,D,C,B,A,p,o;y[z>>5]|=128<<(24-z%32);y[((z+64>>9)<<4)+15]=z;for(var B=0;B<y.length;B+=16){K=r[0];J=r[1];I=r[2];G=r[3];F=r[4];E=r[5];D=r[6];C=r[7];for(var A=0;A<64;A++){if(A<16){s[A]=y[A+B]}else{var n=s[A-15],u=s[A-2],M=((n<<25)|(n>>>7))^((n<<14)|(n>>>18))^(n>>>3),L=((u<<15)|(u>>>17))^((u<<13)|(u>>>19))^(u>>>10);s[A]=M+(s[A-7]>>>0)+L+(s[A-16]>>>0)}var t=F&E^~F&D,k=K&J^K&I^J&I,x=((K<<30)|(K>>>2))^((K<<19)|(K>>>13))^((K<<10)|(K>>>22)),v=((F<<26)|(F>>>6))^((F<<21)|(F>>>11))^((F<<7)|(F>>>25));p=(C>>>0)+v+t+(a[A])+(s[A]>>>0);o=x+k;C=D;D=E;E=F;F=G+p;G=I;I=J;J=K;K=p+o}r[0]+=K;r[1]+=J;r[2]+=I;r[3]+=G;r[4]+=F;r[5]+=E;r[6]+=D;r[7]+=C}return r};d._blocksize=16})();

function Newpost(element) { // listens textarea and adds some methods to it
    this.textarea = element;
    this.insert = function(text) {
        var textarea = this.textarea;
    	if (textarea) {
    		if (textarea.createTextRange && textarea.caretPos) { // IE
    			var caretPos = textarea.caretPos;
    			caretPos.text = caretPos.text.charAt(caretPos.text.length-1) == " " ? text + " " : text;
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

function getSelText() {
    document.aform.selectedtext.value =  window.getSelection();
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
    get rgb() {return this.torgb(this.data)},
    get rgba() {return this.torgba(this.data)},
    get hex() {return this.tohex(this.data.slice(0,3))},
    get hsl() {return this.tohsl(this.data.slice(0,3))},
    
    torgba : function(arr) {
        arr = this.unpack(arguments);
        return 'rgba(' + arr.join(',') + ')';
    },
    
    torgb : function(arr) {
        arr = this.unpack(arguments);
        return 'rgb(' + arr.slice(0,3).join(',') + ')';
    },
    
    tohex : function(arr) {
        arr = this.unpack(arguments);
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
    
    tohsl : function(arr) {
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
    
    unpack : function(arr) {
        return (arr[0] instanceof Array) ? arr[0] : arr;
    },
}

function previewPost(selector) {
    $(selector).hover(function(e) {
        var d = $('<div/>');
        e.preventDefault();
    });
}

function labelsToPlaceholders(list) {
    for (var i=0; i < list.length; i++) {
        var x = list[i],
            t = $('label[for="'+x+'"]').text(),
            dt = $('.' + x + '-d').find('dt').hide(),
            dd = $('#' + x);
        dd.attr('placeholder', t);
    }
    if ($('.bbcode').css('display') === 'none') {
        $('.captcha-d').css({marginTop : 1})
    }
}

function manipulator(arr) { // manipulates elements. Used for custom user styles.
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

// make page changes, that can't be afforded through CSS
function styleDOM(style) {

}

function parseQs(key) { // query string parser
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

function regChangeEvent(id, func) {
    $('#'+id).change(function(e) {
        //console.log(this.value, func)
        func(this.value)
    });
}

function resetSettings() {
    // TODO
}

function slideRemove(elem) {
    elem.slideUp(600, function() {
        $(this).remove();
    });
}

function init() {
    var textArea = new Newpost($('.message')[0]),
        set = $.settings('hideSectGroup');
    
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
    
    $('.deleteMode > input').click(function(x) {
        var tmp = this.value,
            t = $(this),
            fn;
        this.value = t.data('back');
        t.data('back', tmp);
        t.next().toggle();
        if (t.attr('class') == 'toggled') {
            t.removeClass('toggled');
            t.addClass('toggle');
        } else {
            t.removeClass('toggle');
            t.addClass('toggled');
        }
    });
    
    // Posts deletion
    $('#main').delegate('.post', 'click', function(event) {
        if ($('.deleteMode input').attr('class') !== 'toggled') {
            return true;
        }
        var post = $(this).addClass('deleted'),
            id = post.data('id'),
            password = Crypto.SHA256($('#password').val());
        
        $.ajax({
            'url': '/api/post/' + id + '?password=' + password,
            'type': 'DELETE',
        })
        .error(function(data) {
            $.message('error', $.parseJSON(data.responseText)['detail']);
            post.removeClass('deleted');
        })
        .success(function(data) {
            if (post.prev().length !== 0) {
                // post is not first in thread
                slideRemove(post);
                return true;
            }
            
            // remove whole thread
            if (currentPage.type === 'thread') {
                window.location.href = './';
                return true;
            }
            var thread = post.parent();
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
            textArea.insert('>>' + e.srcElement.innerHTML + ' ');
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
        settings = $('.settings dd').find('select, input'),
        changes = { // description of all functions on settings pages
            'ustyle' : function(x) {
                $('html').attr('id', x);
            },
            
            'hideSidebar' : function(x) {
                var margin = (x) ? '10px' : '200px';

                $('#sidebar').toggle(0, null, function(x) {
                    $('#container-wrap > *').css({'marginLeft' : margin});
                });
            },

            'hideNav' : function(x) {
                $('nav').toggle();
            },

            'hideSectBanner' : function(x) {
                $('.section-banner').toggle();
            },
            
            'newForm' : function(x) {
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
            
            'hideBBCodes' : function(x) {
                $('.bbcode').hide();
            },
        };
        
    for (var x in s) {
        $.settings(x, s[x]);
    }
    
    settings.each(function(x) {
        var s = $.settings(this.id), t;
        if (!!(t = parseQs(this.id))) {
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
                this.checked = s
            }
        }
    });
    
    
    settings.change(function(event) {
        var value = this.value;
        if (this.checked === null) {
            value = (this.checked === 'false') ? '' : this.checked;
        }
        console.log('Setting "' + this.id + '" changed to ', value);
        $.settings(this.id, value);
    });
    
    $('.hideSidebar').click(function(e) {
        e.preventDefault();
        var k = 'hideSidebar',
            c = $.settings(k),
            v = c == '' ? 'on' : '',
            f = changes[k];
        f($.settings('hideSidebar', v));
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
        ul.slideToggle(500);
    });
    
    for (var id in changes) {
        var func = changes[id],
            c = $.settings(id);
        regChangeEvent(id, func);
        if (c) {
            func(id);
        }
    }
}

function initStyle() {
    var key = 'ustyle',
        cookie = $.settings(key);
    
    if (!cookie) {
        return false;
    }
    
    $('html').attr('id', cookie);
    
    return true;
}

function initStorage() {
    var status = ('localStorage' in window && window['localStorage'] !== null),
        key = 'visitedThreads', 
        visitedList = $('.' + key),
        thread, storage, elem, tpl, ul, div;
    
    $('#dontLogVisits').click(function(event) {
        visitedList.slideToggle();
    });
    
    if (!status || $.settings('dontLogVisits')) {
        return false;
    }
    
    storage = $.storage(key) ? $.storage(key) : {};
    
    if (currentPage.type == 'thread') {
        thread = currentPage.thread;
        if (!(thread in storage)) {
            storage[thread] = { 
                'op_post': currentPage.op_post, 
                'section': currentPage.section,
                'visits': 1,
                'title': $('article:first-child .title').text(),
                'description': $.trim($('article:first-child .text').text())
                                .substring(0, 100) + '...',
            };
        } else {
            storage[thread]['visits']++;
        }
        $.storage('visitedThreads', storage);
    } else if (currentPage.type == 'settings') {
        ul = visitedList.find('ul');
        visitedList.show();
        for (var i in storage) {
            var a = $('<a/>');
            item = storage[i];
            elem = $('<li/>');
            // elem.data('visits', item.visits);
            tpl = '/'+item.section+'/'+item.op_post;
            a.attr('href', tpl);
            a.text(tpl + ': ' + item.description);
            ul.append(elem.append(a));
        }
        $('.sortVisitedThreads').click(function(event) {
            
        });
        $('.clearVisitedThreads').click(function(event) {
            event.preventDefault();
            $.storage(key, 0, true); // flush storage
            ul.children('li').slideUp('normal', function() {
                $(this).remove();
            });
        });
    }
}

function initHotkeys() {
    $('.new-post input, .new-post textarea').keydown('shift+return', function(event) {
        $('.new-post').submit();
        return false;
    });
}

function initAJAX() {
    if ($.settings('noAJAX')) {
        return false;
    }
    $('.new-post').submit(function(event) {
        event.preventDefault();
        var data = $(this).serialize(),
            page = '/api/post/';

        $.post(page, data)
            .error(function(data) {
                //document.write(data.responseText); // for debugging
                var rt = $.parseJSON(data.responseText)['field-errors'],
                    t = [], l;
                for (var i in rt) {
                    // Get label text of current field
                    l = $('label[for="'+i+'"]').text();
                    t.push(l + ': ' + rt[i].join(', '));
                }
                $.message('error', t.join('<br/>'));
            })
            .success(function(data) {
                if (!$.settings('hideNotifications')) {
                    $.message('notice', 'Ваше сообщение отправлено.');
                }
                if (currentPage.type == 'section') { // redirect
                    window.location.href += data.pid;
                    return true;
                }
                $(data.html).hide().appendTo('.thread').fadeIn(500);
                try {
                    window.location.hash = 'post' + data.pid;
                } catch(e) {}
                $('.captcha-img').trigger('click');
                $('.new-post').insertBefore('.threads');
                $('.new-post').find(':input').each(function() {
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
            });
    });
}

$(init);
$(initSettings);
$(initStyle);
$(initStorage);
$(initHotkeys);
$(initAJAX);