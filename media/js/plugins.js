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
     * Copyright (c) 2011, Paul Bagwell <about.me/pbagwl>.
     * Dual licensed under the MIT and GPL licenses:
     * http://www.opensource.org/licenses/mit-license.php
     * http://www.gnu.org/licenses/gpl.html
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
     * Copyright (c) 2011, Paul Bagwell <about.me/pbagwl>.
     * Dual licensed under the MIT and GPL licenses:
     * http://www.opensource.org/licenses/mit-license.php
     * http://www.gnu.org/licenses/gpl.html
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
    
});

// Prototype plugins
    $.fn.sort = function(sortAttr, sortDesc) {
	//Must Specify Sort Attribute
        if (typeof (sortAttr) === "undefined") {
            return $(this);
        }
        if (sortAttr == "") {
            return $(this);
        }

	//If sort attribute is a single string such as "name"
        if (typeof (sortAttr) === "string") {

            var retObj = $(this).get().sort(function(a, b) {
		//Sort numeric values
                if (typeof ($(a).attr(sortAttr)) === "number") {

                    return parseInt($(a).attr(sortAttr)) > parseInt($(b).attr(sortAttr)) ? 1 : -1;
                }
		//sort string values
                else {
                    return $(a).attr(sortAttr).toLowerCase() > $(b).attr(sortAttr).toLowerCase() ? 1 : -1;
                }
            });
	    //If sort is descending
            if (getSort(sortDesc)) {
                return $(retObj.reverse());
            }
            else {
                return $(retObj);
            }
        }
	//If data is an object such as a returned JSON object
        if (typeof (sortAttr) === "object") {
	    //If the sort attribute is an Array  i.e. ["Name", "Phone","Foo"] , this will sort based on that order.
            if ((sortAttr).length) {
                var retObj = $(this).get().sort(function(a, b) {
                    var i = 0;
                    var retval = 1;
                    while (i < sortAttr.length) {
                        var al = $(a).attr(sortAttr[i]).toLowerCase();
                        var bl = $(b).attr(sortAttr[i]).toLowerCase();

                        if (al > bl) { retval = 1; break; }
                        if (bl > al) { retval = -1; break; }
                        i++;
                    }
                    return retval;

                });
                if (getSort(sortDesc)) {
                    return $(retObj.reverse());
                }
                else {
                    return $(retObj);
                }
            }
 	    //Sort object based on single sort attribute
            else {
                var retObj = $(this).get().sort(function(a, b) {
                    var attrLen = 0;
                    for (var v in sortAttr) {
                        var al = $(a).attr(v).toLowerCase();
                        var bl = $(b).attr(v).toLowerCase();
                        if (al > bl) { return (getSort(sortAttr[v])) ? -1 : 1; }
                        if (bl > al) { return (getSort(sortAttr[v])) ? 1 : -1; }
                    }

                });
                if (getSort(sortDesc)) {
                    return $(retObj.reverse());
                }
                else {
                    return $(retObj);
                }

            }
        }
    }

	//Determines if the sort should be Ascending(false) or Descending(true)
	//Can determine based on Boolean Value or String
    function getSort(sortDesc) {
        if (typeof sortDesc == "boolean") {
            return sortDesc;
        }
        else if (sortDesc.toLowerCase() == "desc") {
            return true;
        }
	//Incase boolean value gets passed as string
        else if (sortDesc.toLowerCase() == "true") {
            return true;
        }
        else return false;
    };
    

})(jQuery);