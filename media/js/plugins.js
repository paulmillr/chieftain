// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
    log.history = log.history || [];   // store logs to an array for reference
    log.history.push(arguments);
    if (this.console) console.log( Array.prototype.slice.call(arguments) );
};
(function() {
    if (!window.gettext) {
        window.gettext = function(text) {
            return text;
        };
    }
    gettext('Settings error');
})();

// catch all document.write() calls
(function(doc) {
    var write = doc.write;
    doc.write = function(q) {
        if (/docwriteregexwhitelist/.test(q)) {
            write.apply(doc, arguments);
        }
    };
})(document);

/*
 * Crypto-JS v2.0.0
 * http://code.google.com/p/crypto-js/
 * Copyright (c) 2009, Jeff Mott. All rights reserved.
 * http://code.google.com/p/crypto-js/wiki/License
 */

(function ($) {
$.extend({
    /**
     * Cookie plugin
     *
     * Copyright (c) 2006 Klaus Hartl (stilbuero.de)
     * Dual licensed under the MIT and GPL licenses:
     * http://www.opensource.org/licenses/mit-license.php
     * http://www.gnu.org/licenses/gpl.html
     *
     */
    cookie: function(name, value, options) {
        if (typeof value !== 'undefined') { // name and value given, set cookie
            options = options || {};
            var path = options.path ? '; path=' + (options.path) : '; path=/',
                domain = options.domain ? '; domain=' + (options.domain) : '',
                secure = options.secure ? '; secure' : '',
                expires = '';
            if (value === null) {
                value = '';
                options.expires = -1;
            }
            if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
                var date;
                if (typeof options.expires == 'number') {
                    date = new Date();
                    date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
                } else {
                    date = options.expires;
                }
                expires = '; expires=' + date.toUTCString();
            }
            document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
            return value;
        } else { // only name given, get cookie
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = $.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    },

    settings: function(name, value) {
        var elem = $('body');
        if (typeof name === 'undefiled') {
            return elem.attr('class').split(' ');
        } else if (typeof value === 'undefined') {
            switch (name) {
                case 'style': return $('html').attr('id'); break;
                default: return elem.hasClass(name); break;
            }
        } else {
            switch (name) {
                case 'style': $('html').attr('id', value); break;
                default: elem.toggleClass(name); break;
            }
            if (value === 'false' || value === false) {
                value = '';
            }
            $.post(window.api.url + '/settings/' + name, {'data': value})
            .error(function(xhr) {
                $.notification('error', gettext('Settings error'));
            });
        }
    },

    // Little wrapper around $.cookie
    localSettings: function(name, value) {
        return $.cookie(name, value);
    },

    /**
     * HTML5 Local storage jquery class.
     * 
     * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
     * Licensed under the MIT license:
     * http://www.opensource.org/licenses/mit-license.php
     */
    storage: function(name, value, mode) {
        var res,
            st = window.localStorage;

        if (!st) {
            return false;
        }

        name = 'k_' + name;
        if (mode === 'flush') {
            st.setItem(name, '');
            return true;
        }
        if (value === undefined) {
            res = st.getItem(name);
            try {
                res = JSON.parse(res);
            } catch(e) {}

            return res;
        } else {
            st.setItem(name, JSON.stringify(value));
            return value;
        }
    },

    /**
     * Canvas color picker class.
     * 
     * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
     * Licensed under the MIT license:
     * http://www.opensource.org/licenses/mit-license.php
     * @param {String} image Link to the image, that would serve as a picker
     * @param {String} canvas Canvas element ID
     * @param {String} current Background color of this element will change
     * on moving across.
     * @param {Function} callback Function, that would be executed 
     * after clicking on the picker.
     */
    colorPicker: function(image, canvas, current, callback) {
        var cp = document.getElementById(canvas).getContext('2d'),
            out = $('#'+current),
            canv = $('#'+canvas),
            img = new Image(),
            self = this;
        this.color = new ColorContainer()

        img.src = image;
        img.onload = function() {
            cp.drawImage(img, 0, 0);
        }

        function colorMeter(event, type) {
            var x = event.pageX - event.currentTarget.offsetLeft,
                y = event.pageY - event.currentTarget.offsetTop,
                ctx = document.getElementById(canvas).getContext('2d'),
                imgd = ctx.getImageData(x, y, 1, 1),
                data = imgd.data;

            return new ColorContainer(data[0], data[1], data[2], data[3]);
        }

        $(canv).mousemove(function(event) {
            out.css({'backgroundColor' : colorMeter(event).rgba});
        });

        $(canv).mousedown(function(event) {
            self.color = colorMeter(event);
            callback(self.color);
        });
    },

    /**
     * Canvas drawer class.
     * 
     * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
     * Licensed under the MIT license:
     * http://www.opensource.org/licenses/mit-license.php
     */
    drawer: function(canvas, saveButton, saveCallback) {
        var c = document.getElementById(canvas).getContext('2d'),
            ca = $('#'+canvas),
            pos = transform,
            self = this;
        this.lastpos = {x : -1, y : -1};
        this.draw = false;
        this.color = new ColorContainer();
        this.width = 4.0;

        function transform(event) {
            if (event.offsetX) { // firefox doesn't support offsetX
                return {x : event.offsetX, y : event.offsetY};
            }
            return {x : event.layerX, y : event.layerY};
        }

        ca.mousemove(function(event) {
            if (!self.draw) {
                return false;
            }
            //window.log(event)
            var pos = transform(event);
            c.strokeStyle = self.color.rgba;
            c.lineWidth = self.width;
            //c.lineJoin = 'round';
            c.beginPath();
            //window.log(self.lastpos)
            c.moveTo(self.lastpos.x, self.lastpos.y);
            c.lineTo(pos.x, pos.y);
            c.closePath();
            c.stroke();
            self.lastpos = pos;
        });

        ca.mousedown(function(event) {
            self.draw = true;
            self.lastpos = transform(event)
        });

        ca.mouseup(function(event) {
            self.draw = false;
        });

        ca.bind('selectstart', function(event) { // disable 'text selection' on canvas
            event.preventDefault();
            event.target.style.cursor = 'crosshair';
        });

        $(saveButton).click(function(event) {
            event.preventDefault();
            saveCallback(ca[0].toDataURL());
        });
    },

    /**
     * Copyright 2010 (c) akquinet.
     *
     * jQuery notification plugin is based on code of jquery.toastmessage, 
     * modified by Paul Bagwell.
     *
     * Licensed under the Apache License, Version 2.0 (the "License");
     * you may not use this file except in compliance with the License.
     * You may obtain a copy of the License at
     * http://www.apache.org/licenses/LICENSE-2.0
     * Unless required by applicable law or agreed to in writing, software
     * distributed under the License is distributed on an "AS IS" BASIS,
     * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     * See the License for the specific language governing permissions and
     * limitations under the License.
     */
    notification: function(type, message, options) {
        var defaultSettings = {
            inEffect: {opacity: 'show'}, // in effect
            inEffectDuration: 600, // in effect duration in ms
            stayTime: 3000, // time in miliseconds before the item has to disappear
            text: '',    // content of the item
            sticky: false, // should the notification item be sticky or not?
            type: 'notice', // notice, warning, error, success
            position: 'top-right', // top-right, center, middle-bottom etc
            closeText: '', // text which will be shown as close button, 
                           // set to '' when you want to introduce an image via css
            close: null // callback function when the message is closed
        };

        function init(options) {
            if (options) {
                $.extend(defaultSettings, options);
            }
        }

        function remove(obj, options) {
            obj.animate({opacity: '0'}, 600, function() {
                obj.parent().animate({height: '0px'}, 300, function() {
                    obj.parent().remove();
                });
            });
            // callback
            if (options && options.close !== null) {
                options.close();
            }
        }

        function show(options) {
            var localSettings = $.extend(defaultSettings, options),
                notificationWrapAll = (!$('.notification-container').length) ? 
                    $('<div/>').addClass('notification-container')
                    .addClass('notification-position-' + localSettings.position)
                    .appendTo('body') 
                    : $('.notification-container'), 
                notificationItemOuter = $('<div/>').addClass('notification-item-wrapper'), 
                notificationItemInner = $('<div/>').hide()
                    .addClass('notification-item notification-type-' + localSettings.type)
                    .appendTo(notificationWrapAll)
                    .html('<p>' + localSettings.text + '</p>')
                    .animate(localSettings.inEffect, localSettings.inEffectDuration)
                    .wrap(notificationItemOuter), 
                notificationItemClose = $('<div/>')
                    .addClass('notification-item-close')
                    .prependTo(notificationItemInner)
                    .html(localSettings.closeText)
                    .click(function() {
                        remove(notificationItemInner, localSettings);
                    }),
                notificationItemImage = $('<div/>').addClass('notification-item-image')
                    .addClass('notification-item-image-' + localSettings.type)
                    .prependTo(notificationItemInner);

            if (navigator.userAgent.match(/MSIE 6/i)) {
                notificationWrapAll.css({top: document.documentElement.scrollTop});
            }

            if (!localSettings.sticky) {
                setTimeout(function() {
                    remove(notificationItemInner, localSettings);
                },
                localSettings.stayTime);
            }
            return notificationItemInner;
        }

        if (!message) {
            message = type;
            type = 'notice';
        }

        return show({
            'text': message, 
            'type': type || 'notice'
        });
    },

    /**
     * jQuery desktop notification class.
     * 
     * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
     * Licensed under the MIT license:
     * http://www.opensource.org/licenses/mit-license.php
     */
    dNotification: {
        n: window.webkitNotifications,
        show: function(text, timeout, title, icon) {
            if (!timeout) timeout = 3000;
            if (!title) {
                title = $.trim($('title').text());
            }
            if (!icon) {
                icon = $('link[rel="apple-touch-icon"]').attr('href');
            }

            instance = this.n.createNotification(icon, title, text);
            instance.show();
            setTimeout(function() {instance.cancel()}, timeout);
        },

        request: function(callback) {
            if (!callback) callback = function() {};
            if (!this.checkSupport()) {
                return false;
            }
            this.n.requestPermission(callback);
        },

        check: function() {
            return (this.checkSupport() && this.n.checkPermission() === 0);
        },
        
        checkSupport: function() {
            return !!this.n;
        }
    },

    /**
     * jQuery multipart uploader class.
     * 
     * Copyright (c) 2011, Paul Bagwell <pbagwl.com>.
     * Licensed under the MIT license:
     * http://www.opensource.org/licenses/mit-license.php
     */
    mpu: function(uri, form) {
        function MultipartUploader(uri, form) {
            if (typeof form === 'string') {
                form = $(form);
            }

            this.uri = uri;
            this.form = form;
            this.send();
        }

        $.extend(MultipartUploader.prototype, {
            boundary : 'gc0p4Jq0M2Yt08jU534c0p',
            errorCallback: function(data) {},
            successCallback: function(data) {},
            error: function(callback) {
                this.errorCallback = callback;
                return this;
            },

            success: function(callback) {
                this.successCallback = callback;
                return this;
            },

            makeMultipartItem: function(name, value) {
                var res = '';
                res += '--' + this.boundary + '\r\n';
                res += 'Content-Disposition: form-data; ';
                res += 'name="'+name+'"\r\n\r\n';
                res += value + '\r\n';
                return res;
            },

            serializedToMultipart: function(list) {
                // convert jQuery.serializeArray(arr) to multipart data
                var res = '';
                for (var i=0; i < list.length; i++) {
                    res += this.makeMultipartItem(list[i]['name'], list[i]['value']);
                }
                return res;
            },

            fileToMultipart: function(fileInput, callback) {
                var files = fileInput.attr('files'),
                    fr = new FileReader(),
                    file = files[0],
                    self = this;

                if (!file) {
                    return callback('');
                }

                function wrapFile(fileData) {
                    var res = '';
                    res += '--' + self.boundary + '\r\n'
                    res += 'Content-Disposition: form-data; name="' + fileInput.attr('id') + '"; ';
                    res += 'filename="' + file.name + '"\r\n';
                    res += 'Content-Type: ' + file.type + '\r\n\r\n';
                    res += fileData + '\r\n';
                    res += '--' + self.boundary + '--\r\n';
                    return res
                }

                fr.onload = function(event) {
                    if (event.loaded !== event.total) {
                        return false;
                    }
                    callback(wrapFile(event.currentTarget.result));
                };

                fr.readAsBinaryString(file);
            },

            send: function() {
                var fr = new FileReader(),
                    xhr = new XMLHttpRequest(),
                    body = '', // request body
                    self = this,
                    fileInput = this.form.find('input[type="file"]:first');

                xhr.open('POST', this.uri, true);
                xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + this.boundary);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4) {
                        if (xhr.status >= 200 && xhr.status < 400) {
                            self.successCallback($.parseJSON(xhr.responseText));
                        } else {
                            self.errorCallback(xhr);
                        }
                    }
                };
                body += this.serializedToMultipart(this.form.serializeArray());
                this.fileToMultipart(fileInput, function(fileData) {
                    body += fileData;

                    if (xhr.sendAsBinary) { // native support by Firefox
                        xhr.sendAsBinary(body);
                    } else if (Uint8Array) { // use FileWriter API in Chrome
                        var blob = new BlobBuilder(),
                            arrb = new ArrayBuffer(body.length),
                            ui8a = new Uint8Array(arrb, 0);
                        for (var i=0; i < body.length; i++) {
                            ui8a[i] = (body.charCodeAt(i) & 0xff);
                        }
                        blob.append(arrb);
                        xhr.send(blob.getBlob());
                    } else { // send raw data
                        xhr.send(body);
                    }

                });
                return this;
            }
        });

        return new MultipartUploader(uri, form);
    }
});

jQuery.each(["put", "delete"], function( i, method ) {
	jQuery[ method ] = function( url, data, callback, type ) {
		// shift arguments if data argument was omitted
		if ( jQuery.isFunction( data ) ) {
			type = type || callback;
			callback = data;
			data = undefined;
		}

		return jQuery.ajax({
			type: method,
			url: url,
			data: data,
			success: callback,
			dataType: type
		});
	};
});

/*
 * jQuery Hotkeys Plugin
 * Copyright 2010, John Resig
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Based upon the plugin by Tzury Bar Yochay:
 * http://github.com/tzuryby/hotkeys
 *
 * Original idea by:
 * Binny V A, http://www.openjs.com/scripts/events/keyboard_shortcuts/
*/
jQuery.hotkeys = {
	version: "0.8",

	specialKeys: {
		8: "backspace", 9: "tab", 13: "return", 16: "shift", 17: "ctrl", 18: "alt", 19: "pause",
		20: "capslock", 27: "esc", 32: "space", 33: "pageup", 34: "pagedown", 35: "end", 36: "home",
		37: "left", 38: "up", 39: "right", 40: "down", 45: "insert", 46: "del", 
		96: "0", 97: "1", 98: "2", 99: "3", 100: "4", 101: "5", 102: "6", 103: "7",
		104: "8", 105: "9", 106: "*", 107: "+", 109: "-", 110: ".", 111 : "/", 
		112: "f1", 113: "f2", 114: "f3", 115: "f4", 116: "f5", 117: "f6", 118: "f7", 119: "f8", 
		120: "f9", 121: "f10", 122: "f11", 123: "f12", 144: "numlock", 145: "scroll", 191: "/", 224: "meta"
	},

	shiftNums: {
		"`": "~", "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", 
		"8": "*", "9": "(", "0": ")", "-": "_", "=": "+", ";": ": ", "'": "\"", ",": "<", 
		".": ">",  "/": "?",  "\\": "|"
	}
};

function keyHandler( handleObj ) {
	// Only care when a possible input has been specified
	if ( typeof handleObj.data !== "string" ) {
		return;
	}

	var origHandler = handleObj.handler,
		keys = handleObj.data.toLowerCase().split(" ");

	handleObj.handler = function( event ) {
		// Don't fire in text-accepting inputs that we didn't directly bind to
		if ( this !== event.target && (/textarea|select/i.test( event.target.nodeName ) ||
			 event.target.type === "text") ) {
			return;
		}

		// Keypress represents characters, not special keys
		var special = event.type !== "keypress" && $.hotkeys.specialKeys[ event.which ],
			character = String.fromCharCode( event.which ).toLowerCase(),
			key, modif = "", possible = {};

		// check combinations (alt|ctrl|shift+anything)
		if ( event.altKey && special !== "alt" ) {
			modif += "alt+";
		}

		if ( event.ctrlKey && special !== "ctrl" ) {
			modif += "ctrl+";
		}

		// TODO: Need to make sure this works consistently across platforms
		if ( event.metaKey && !event.ctrlKey && special !== "meta" ) {
			modif += "meta+";
		}

		if ( event.shiftKey && special !== "shift" ) {
			modif += "shift+";
		}

		if ( special ) {
			possible[ modif + special ] = true;

		} else {
			possible[ modif + character ] = true;
			possible[ modif + $.hotkeys.shiftNums[ character ] ] = true;

			// "$" can be triggered as "Shift+4" or "Shift+$" or just "$"
			if ( modif === "shift+" ) {
				possible[ $.hotkeys.shiftNums[ character ] ] = true;
			}
		}

		for ( var i = 0, l = keys.length; i < l; i++ ) {
			if ( possible[ keys[i] ] ) {
				return origHandler.apply( this, arguments );
			}
		}
	};
}

$.each([ "keydown", "keyup", "keypress" ], function() {
	$.event.special[ this ] = { add: keyHandler };
});

$.fn.hasScrollBar = function() {
    return this.get(0).scrollHeight - 1 > this.height();
};

})(jQuery);

/*
 * Horizontal Bar Graph for jQuery
 * version 0.1a
 *
 * http://www.dumpsterdoggy.com/plugins/horiz-bar-graph
 *
 * Copyright (c) 2009 Chris Missal
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 */
(function($) {
	$.fn.horizontalBarGraph = function(options) {
	
		var opts = $.extend({}, $.fn.horizontalBarGraph.defaults, options);
		
		this.children("dt,dd").each(function(i) {
		
			var el = $(this);
			if(el.is("dt")) {
				el.css({display: "block", float: "left", clear: "left"}).addClass("hbg-label"); return;
			} else {
				(isTitleDD(el) && opts.hasTitles ? createTitle : createBar)(el, opts);
			}
			setBarHover(el, opts);
		});
		
		tryShowTitle(this);
		
		if(opts.animated) {
			createShowButton(opts, this).insertBefore(this);
		}
		if(opts.colors.length) {
			setColors(this.children("dd"), opts);
		}
		if(opts.hoverColors.length) {
			setHoverColors(this.children("dd"), opts);
		}
		
		scaleGraph(this);
		
		return this;
	};
	
	function scaleGraph(graph) {
		var maxWidth = 0;
		graph.children("dt").each(function() {
			maxWidth = Math.max($(this).width(), maxWidth);
		}).css({width: maxWidth+"px"});
	}
	
	function setBarHover(bar, opts) {
		bar.hover(function() {
			bar.addClass("hbg-bar-hover");
		}, function() {
			bar.removeClass("hbg-bar-hover");
		});
	}
	
	function createShowButton(opts, graph) {
		var button = $("<span />").text(opts.button).addClass("hbg-show-button");
		button.click(function() {
			graph.children("dd").show('slow', function() { button.fadeOut('normal'); });
		});
		return button;
	}
	
	function createBar(e, opts) {
		var val = e.text();
		e.css({marginLeft: e.prev().is("dt") ? "5px" : "0px", width: Math.floor(val/opts.interval)+"px"});
		e.html($("<span/>").html(val).addClass("hbg-value"));
		applyOptions(e, opts);
	}
	
	function createTitle(e, opts) {
		var title = e.text();
		e.prev().attr("title", title);
		e.remove();
	}
	
	function tryShowTitle(graph) {
		var title = graph.attr("title");
		if(title) {
			$("<div/>").text(title).addClass("hbg-title").insertBefore(graph);
			graph.css({overflow: "hidden"});
		}
	}
	
	function setColors(bars, opts) {
		var i = 0;
		bars.each(function() { 
			var c = i++ % opts.colors.length;
			$(this).css({backgroundColor: opts.colors[c]});
		});
	}
	
	function setHoverColors(bars, opts) {
		var i = 0;
		bars.each(function(i) {
			var bar = $(this);
			var c = bar.css("background-color");
			var hc = opts.hoverColors[i++ % opts.hoverColors.length];
			bar.hover(function() {
				$(this).css({backgroundColor: hc});
			}, function() {
				$(this).css({backgroundColor: c});
			});
		});
	}
	
	function applyOptions(e, opts) {
		e.css({float: "left"}).addClass("hbg-bar");
		if(opts.animated) { e.hide(); }
	}
	
	function isTitleDD(e) {
		return (e.is(":even") && e.prev().is("dd"));
	}
	
	$.fn.horizontalBarGraph.defaults = {
		interval: 1,
		hasTitles: false,
		animated: false,
		button: 'Show Values',
		colors: [],
		hoverColors: []
	};
	
})(jQuery);

/*
jQuery Placeholder 1.1.1

Copyright (c) 2010 Michael J. Ryan (http://tracker1.info/)

Dual licensed under the MIT and GPL licenses:
	http://www.opensource.org/licenses/mit-license.php
	http://www.gnu.org/licenses/gpl.html
*/
(function(a){function f(){var b=a(this);a(b.data(e)).css("display","none")}function i(){var b=this;setTimeout(function(){var c=a(b);a(c.data(e)).css("top",c.position().top+"px").css("left",c.position().left+"px").css("display",c.val()?"none":"block")},200)}var e="PLACEHOLDER-LABEL",j=false,k={labelClass:"placeholder"},g=document.createElement("input");if("placeholder"in g){a.fn.placeholder=a.fn.unplaceholder=function(){};delete g}else{delete g;a.fn.placeholder=function(b){if(!j){a(".PLACEHOLDER-INPUT").live("click",
f).live("focusin",f).live("focusout",i);j=bound=true}var c=a.extend(k,b);this.each(function(){var l=Math.random().toString(32).replace(/\./,""),d=a(this),h=a('<label style="position:absolute;display:none;top:0;left:0;"></label>');if(!(!d.attr("placeholder")||d.data("PLACEHOLDER-INPUT")==="PLACEHOLDER-INPUT")){d.attr("id")||(d.attr("id")="input_"+l);h.attr("id",d.attr("id")+"_placeholder").data("PLACEHOLDER-INPUT","#"+d.attr("id")).attr("for",d.attr("id")).addClass(c.labelClass).addClass(c.labelClass+
"-for-"+this.tagName.toLowerCase()).addClass(e).text(d.attr("placeholder"));d.data(e,"#"+h.attr("id")).data("PLACEHOLDER-INPUT","PLACEHOLDER-INPUT").addClass("PLACEHOLDER-INPUT").after(h);f.call(this);i.call(this)}})};a.fn.unplaceholder=function(){this.each(function(){var b=a(this),c=a(b.data(e));if(b.data("PLACEHOLDER-INPUT")==="PLACEHOLDER-INPUT"){c.remove();b.removeData("PLACEHOLDER-INPUT").removeData(e).removeClass("PLACEHOLDER-INPUT")}})}}})(jQuery);


/*!
 * jQuery Form Plugin
 * version: 2.67 (12-MAR-2011)
 * @requires jQuery v1.3.2 or later
 *
 * Examples and documentation at: http://malsup.com/jquery/form/
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 */
(function(a){function b(){if(a.fn.ajaxSubmit.debug){var b="[jquery.form] "+Array.prototype.join.call(arguments,"");window.console&&window.console.log?window.console.log(b):window.opera&&window.opera.postError&&window.opera.postError(b)}}a.fn.ajaxSubmit=function(c){function r(){function t(){if(!j.aborted){var c=i.contentWindow?i.contentWindow.document:i.contentDocument?i.contentDocument:i.document;if(!c||c.location.href==e.iframeSrc)return;i.detachEvent?i.detachEvent("onload",t):i.removeEventListener("load",t,!1);var d=!0;try{if(m)throw"timeout";var f=e.dataType=="xml"||c.XMLDocument||a.isXMLDoc(c);b("isXml="+f);if(!f&&window.opera&&(c.body==null||c.body.innerHTML=="")&&--s){b("requeing onLoad callback, DOM not available"),setTimeout(t,250);return}j.responseText=c.body?c.body.innerHTML:c.documentElement?c.documentElement.innerHTML:null,j.responseXML=c.XMLDocument?c.XMLDocument:c,j.getResponseHeader=function(a){var b={"content-type":e.dataType};return b[a]};var g=/(json|script)/.test(e.dataType);if(g||e.textarea){var l=c.getElementsByTagName("textarea")[0];if(l)j.responseText=l.value;else if(g){var n=c.getElementsByTagName("pre")[0],o=c.getElementsByTagName("body")[0];n?j.responseText=n.textContent:o&&(j.responseText=o.innerHTML)}}else e.dataType=="xml"&&!j.responseXML&&j.responseText!=null&&(j.responseXML=u(j.responseText));q=w(j,e.dataType,e)}catch(p){b("error caught:",p),d=!1,j.error=p,e.error&&e.error.call(e.context,j,"error",p),k&&a.event.trigger("ajaxError",[j,e,p])}j.aborted&&(b("upload aborted"),d=!1),d&&(e.success&&e.success.call(e.context,q,"success",j),k&&a.event.trigger("ajaxSuccess",[j,e])),k&&a.event.trigger("ajaxComplete",[j,e]),k&&!--a.active&&a.event.trigger("ajaxStop"),e.complete&&e.complete.call(e.context,j,d?"success":"error"),setTimeout(function(){h.removeData("form-plugin-onload"),h.remove(),j.responseXML=null},100)}}function p(){var b=l.attr("target"),c=l.attr("action");d.setAttribute("target",f),d.getAttribute("method")!="POST"&&d.setAttribute("method","POST"),d.getAttribute("action")!=e.url&&d.setAttribute("action",e.url),e.skipEncodingOverride||l.attr({encoding:"multipart/form-data",enctype:"multipart/form-data"}),e.timeout&&setTimeout(function(){m=!0,t()},e.timeout);var g=[];try{if(e.extraData)for(var j in e.extraData)g.push(a('<input type="hidden" name="'+j+'" value="'+e.extraData[j]+'" />').appendTo(d)[0]);h.appendTo("body"),i.attachEvent?i.attachEvent("onload",t):i.addEventListener("load",t,!1),d.submit()}finally{d.setAttribute("action",c),b?d.setAttribute("target",b):l.removeAttr("target"),a(g).remove()}}var d=l[0];if(a(":input[name=submit],:input[id=submit]",d).length)alert('Error: Form elements must not have name or id of "submit".');else{var e=a.extend(!0,{},a.ajaxSettings,c);e.context=e.context||e;var f="jqFormIO"+(new Date).getTime(),g="_"+f,h=a('<iframe id="'+f+'" name="'+f+'" src="'+e.iframeSrc+'" />'),i=h[0];h.css({position:"absolute",top:"-1000px",left:"-1000px"});var j={aborted:0,responseText:null,responseXML:null,status:0,statusText:"n/a",getAllResponseHeaders:function(){},getResponseHeader:function(){},setRequestHeader:function(){},abort:function(){b("aborting upload...");var c="aborted";this.aborted=1,h.attr("src",e.iframeSrc),j.error=c,e.error&&e.error.call(e.context,j,"error",c),k&&a.event.trigger("ajaxError",[j,e,c]),e.complete&&e.complete.call(e.context,j,"error")}},k=e.global;k&&!(a.active++)&&a.event.trigger("ajaxStart"),k&&a.event.trigger("ajaxSend",[j,e]);if(e.beforeSend&&e.beforeSend.call(e.context,j,e)===!1){e.global&&a.active--;return}if(j.aborted)return;var m=0,n=d.clk;if(n){var o=n.name;o&&!n.disabled&&(e.extraData=e.extraData||{},e.extraData[o]=n.value,n.type=="image"&&(e.extraData[o+".x"]=d.clk_x,e.extraData[o+".y"]=d.clk_y))}e.forceSync?p():setTimeout(p,10);var q,r,s=50,u=a.parseXML||function(a,b){window.ActiveXObject?(b=new ActiveXObject("Microsoft.XMLDOM"),b.async="false",b.loadXML(a)):b=(new DOMParser).parseFromString(a,"text/xml");return b&&b.documentElement&&b.documentElement.nodeName!="parsererror"?b:null},v=a.parseJSON||function(a){return window.eval("("+a+")")},w=function(b,c,d){var e=b.getResponseHeader("content-type")||"",f=c==="xml"||!c&&e.indexOf("xml")>=0,g=f?b.responseXML:b.responseText;f&&g.documentElement.nodeName==="parsererror"&&a.error&&a.error("parsererror"),d&&d.dataFilter&&(g=d.dataFilter(g,c)),typeof g=="string"&&(c==="json"||!c&&e.indexOf("json")>=0?g=v(g):(c==="script"||!c&&e.indexOf("javascript")>=0)&&a.globalEval(g));return g}}}if(!this.length){b("ajaxSubmit: skipping submit process - no element selected");return this}typeof c=="function"&&(c={success:c});var d=this.attr("action"),e=typeof d=="string"?a.trim(d):"";e&&(e=(e.match(/^([^#]+)/)||[])[1]),e=e||window.location.href||"",c=a.extend(!0,{url:e,type:this[0].getAttribute("method")||"GET",iframeSrc:/^https/i.test(window.location.href||"")?"javascript:false":"about:blank"},c);var f={};this.trigger("form-pre-serialize",[this,c,f]);if(f.veto){b("ajaxSubmit: submit vetoed via form-pre-serialize trigger");return this}if(c.beforeSerialize&&c.beforeSerialize(this,c)===!1){b("ajaxSubmit: submit aborted via beforeSerialize callback");return this}var g,h,i=this.formToArray(c.semantic);if(c.data){c.extraData=c.data;for(g in c.data)if(c.data[g]instanceof Array)for(var j in c.data[g])i.push({name:g,value:c.data[g][j]});else h=c.data[g],h=a.isFunction(h)?h():h,i.push({name:g,value:h})}if(c.beforeSubmit&&c.beforeSubmit(i,this,c)===!1){b("ajaxSubmit: submit aborted via beforeSubmit callback");return this}this.trigger("form-submit-validate",[i,this,c,f]);if(f.veto){b("ajaxSubmit: submit vetoed via form-submit-validate trigger");return this}var k=a.param(i);c.type.toUpperCase()=="GET"?(c.url+=(c.url.indexOf("?")>=0?"&":"?")+k,c.data=null):c.data=k;var l=this,m=[];c.resetForm&&m.push(function(){l.resetForm()}),c.clearForm&&m.push(function(){l.clearForm()});if(!c.dataType&&c.target){var n=c.success||function(){};m.push(function(b){var d=c.replaceTarget?"replaceWith":"html";a(c.target)[d](b).each(n,arguments)})}else c.success&&m.push(c.success);c.success=function(a,b,d){var e=c.context||c;for(var f=0,g=m.length;f<g;f++)m[f].apply(e,[a,b,d||l,l])};var o=a("input:file",this).length>0,p="multipart/form-data",q=l.attr("enctype")==p||l.attr("encoding")==p;c.iframe!==!1&&(o||c.iframe||q)?c.closeKeepAlive?a.get(c.closeKeepAlive,r):r():a.ajax(c),this.trigger("form-submit-notify",[this,c]);return this},a.fn.ajaxForm=function(c){if(this.length===0){var d={s:this.selector,c:this.context};if(!a.isReady&&d.s){b("DOM not ready, queuing ajaxForm"),a(function(){a(d.s,d.c).ajaxForm(c)});return this}b("terminating; zero elements found by selector"+(a.isReady?"":" (DOM not ready)"));return this}return this.ajaxFormUnbind().bind("submit.form-plugin",function(b){b.isDefaultPrevented()||(b.preventDefault(),a(this).ajaxSubmit(c))}).bind("click.form-plugin",function(b){var c=b.target,d=a(c);if(!d.is(":submit,input:image")){var e=d.closest(":submit");if(e.length==0)return;c=e[0]}var f=this;f.clk=c;if(c.type=="image")if(b.offsetX!=undefined)f.clk_x=b.offsetX,f.clk_y=b.offsetY;else if(typeof a.fn.offset=="function"){var g=d.offset();f.clk_x=b.pageX-g.left,f.clk_y=b.pageY-g.top}else f.clk_x=b.pageX-c.offsetLeft,f.clk_y=b.pageY-c.offsetTop;setTimeout(function(){f.clk=f.clk_x=f.clk_y=null},100)})},a.fn.ajaxFormUnbind=function(){return this.unbind("submit.form-plugin click.form-plugin")},a.fn.formToArray=function(b){var c=[];if(this.length===0)return c;var d=this[0],e=b?d.getElementsByTagName("*"):d.elements;if(!e)return c;var f,g,h,i,j,k,l;for(f=0,k=e.length;f<k;f++){j=e[f],h=j.name;if(!h)continue;if(b&&d.clk&&j.type=="image"){!j.disabled&&d.clk==j&&(c.push({name:h,value:a(j).val()}),c.push({name:h+".x",value:d.clk_x},{name:h+".y",value:d.clk_y}));continue}i=a.fieldValue(j,!0);if(i&&i.constructor==Array)for(g=0,l=i.length;g<l;g++)c.push({name:h,value:i[g]});else i!==null&&typeof i!="undefined"&&c.push({name:h,value:i})}if(!b&&d.clk){var m=a(d.clk),n=m[0];h=n.name,h&&!n.disabled&&n.type=="image"&&(c.push({name:h,value:m.val()}),c.push({name:h+".x",value:d.clk_x},{name:h+".y",value:d.clk_y}))}return c},a.fn.formSerialize=function(b){return a.param(this.formToArray(b))},a.fn.fieldSerialize=function(b){var c=[];this.each(function(){var d=this.name;if(!!d){var e=a.fieldValue(this,b);if(e&&e.constructor==Array)for(var f=0,g=e.length;f<g;f++)c.push({name:d,value:e[f]});else e!==null&&typeof e!="undefined"&&c.push({name:this.name,value:e})}});return a.param(c)},a.fn.fieldValue=function(b){for(var c=[],d=0,e=this.length;d<e;d++){var f=this[d],g=a.fieldValue(f,b);if(g===null||typeof g=="undefined"||g.constructor==Array&&!g.length)continue;g.constructor==Array?a.merge(c,g):c.push(g)}return c},a.fieldValue=function(b,c){var d=b.name,e=b.type,f=b.tagName.toLowerCase();c===undefined&&(c=!0);if(c&&(!d||b.disabled||e=="reset"||e=="button"||(e=="checkbox"||e=="radio")&&!b.checked||(e=="submit"||e=="image")&&b.form&&b.form.clk!=b||f=="select"&&b.selectedIndex==-1))return null;if(f=="select"){var g=b.selectedIndex;if(g<0)return null;var h=[],i=b.options,j=e=="select-one",k=j?g+1:i.length;for(var l=j?g:0;l<k;l++){var m=i[l];if(m.selected){var n=m.value;n||(n=m.attributes&&m.attributes.value&&!m.attributes.value.specified?m.text:m.value);if(j)return n;h.push(n)}}return h}return a(b).val()},a.fn.clearForm=function(){return this.each(function(){a("input,select,textarea",this).clearFields()})},a.fn.clearFields=a.fn.clearInputs=function(){return this.each(function(){var a=this.type,b=this.tagName.toLowerCase();a=="text"||a=="password"||b=="textarea"?this.value="":a=="checkbox"||a=="radio"?this.checked=!1:b=="select"&&(this.selectedIndex=-1)})},a.fn.resetForm=function(){return this.each(function(){(typeof this.reset=="function"||typeof this.reset=="object"&&!this.reset.nodeType)&&this.reset()})},a.fn.enable=function(a){a===undefined&&(a=!0);return this.each(function(){this.disabled=!a})},a.fn.selected=function(b){b===undefined&&(b=!0);return this.each(function(){var c=this.type;if(c=="checkbox"||c=="radio")this.checked=b;else if(this.tagName.toLowerCase()=="option"){var d=a(this).parent("select");b&&d[0]&&d[0].type=="select-one"&&d.find("option").selected(!1),this.selected=b}})}})(jQuery)