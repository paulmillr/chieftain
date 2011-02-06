// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
    log.history = log.history || [];   // store logs to an array for reference
    log.history.push(arguments);
    if(this.console) console.log( Array.prototype.slice.call(arguments) );
};

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
    cookie : function(name, value, options) {
        if (typeof value != 'undefined') { // name and value given, set cookie
            options = options || {};
            if (value === null) {
                value = '';
                options.expires = -1;
            }
            var expires = '';
            if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
                var date;
                if (typeof options.expires == 'number') {
                    date = new Date();
                    date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
                } else {
                    date = options.expires;
                }
                expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
            }
            // CAUTION: Needed to parenthesize options.path and options.domain
            // in the following expressions, otherwise they evaluate to undefined
            // in the packed version for some reason...
            var path = options.path ? '; path=' + (options.path) : '';
            var domain = options.domain ? '; domain=' + (options.domain) : '';
            var secure = options.secure ? '; secure' : '';
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
    
    settingsFactory : function(prefix) {
        self = this;
        return function(name, value, options) {
            return self.cookie(prefix + name, value, options);
        }
    },
    
    // Little wrapper around $.cookie
    settings : function(name, value, options) {
        return this.settingsFactory('k_')(name, value, options);
    },
    
    storage : function(name, value, flush) {
        var res;
        name = 'k_' + name;
        if (flush) {
            window.localStorage[name] = ''
            return true;
        }
        if (value === undefined) {
            res = window.localStorage[name];
            try {
                res = JSON.parse(res);
            } catch(e) {}
            
            return res;
        } else {
            window.localStorage[name] = JSON.stringify(value);
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
    colorPicker : function(image, canvas, current, callback) {
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
    drawer : function(canvas, saveButton, saveCallback) {
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
    
    /*
     * Copyright 2010 akquinet
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
    // Based on code of jquery.toastmessage, modified by Paul Bagwell
    message : function(type) {
        var settings = {
            inEffect: {opacity: 'show'}, // in effect
            inEffectDuration: 600, // in effect duration in ms
            stayTime: 3000, // time in miliseconds before the item has to disappear
            text: '',    // content of the item
            sticky: false, // should the toast item sticky or not?
            type: 'notice', // notice, warning, error, success
            position: 'top-right', // top-right, center, middle-bottom etc
            closeText: '', // text which will be shown as close button, 
                           // set to '' when you want to introduce an image via css
            close: null // callback function when the message is closed
        };

        var methods = {
            init : function(options) {
                if (options) {
                    $.extend(settings, options);
                }
            },

            show : function(options) {
                var localSettings = {},
                    toastWrapAll, toastItemOuter, toastItemInner, 
                    toastItemClose, toastItemImage;
                $.extend(localSettings, settings, options);

                toastWrapAll = (!$('.toast-container').length) ? 
                    $('<div/>').addClass('toast-container')
                    .addClass('toast-position-' + localSettings.position)
                    .appendTo('body') 
                    : $('.toast-container');

                toastItemOuter = $('<div/>').addClass('toast-item-wrapper');

                toastItemInner = $('<div/>').hide()
                    .addClass('toast-item toast-type-' + localSettings.type)
                    .appendTo(toastWrapAll)
                    .html('<p>' + localSettings.text + '</p>')
                    .animate(localSettings.inEffect, localSettings.inEffectDuration)
                    .wrap(toastItemOuter);

                toastItemClose = $('<div/>').addClass('toast-item-close')
                    .prependTo(toastItemInner)
                    .html(localSettings.closeText)
                    .click(function() { $.message('remove',toastItemInner, localSettings) });

                toastItemImage = $('<div/>').addClass('toast-item-image')
                    .addClass('toast-item-image-' + localSettings.type)
                    .prependTo(toastItemInner);

                if (navigator.userAgent.match(/MSIE 6/i)) {
                    toastWrapAll.css({top: document.documentElement.scrollTop});
                }

                if (!localSettings.sticky) {
                    setTimeout(function() {
                        $.message('remove', toastItemInner, localSettings);
                    },
                    localSettings.stayTime);
                }
                return toastItemInner;
            },

            notice : function (message) {
                return $.message('show', {text: message, type: 'notice'});
            },

            success : function (message) {
                return $.message('show', {text: message, type: 'success'});
            },

            error : function (message) {
                return $.message('show', {text: message, type: 'error'});
            },

            warning : function (message) {
                return $.message('show', {text: message, type: 'warning'});
            },

            remove: function(obj, options) {
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
        };

        if (methods[type]) {
            return methods[type].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof type === 'object' || ! type) {
            return methods.init.apply(this, arguments);
        }
        return methods['notice'].apply(this, Array.prototype.slice.call(arguments, 0));
    },
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
		var special = event.type !== "keypress" && jQuery.hotkeys.specialKeys[ event.which ],
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
			possible[ modif + jQuery.hotkeys.shiftNums[ character ] ] = true;

			// "$" can be triggered as "Shift+4" or "Shift+$" or just "$"
			if ( modif === "shift+" ) {
				possible[ jQuery.hotkeys.shiftNums[ character ] ] = true;
			}
		}

		for ( var i = 0, l = keys.length; i < l; i++ ) {
			if ( possible[ keys[i] ] ) {
				return origHandler.apply( this, arguments );
			}
		}
	};
}

jQuery.each([ "keydown", "keyup", "keypress" ], function() {
	jQuery.event.special[ this ] = { add: keyHandler };
});


})(jQuery);