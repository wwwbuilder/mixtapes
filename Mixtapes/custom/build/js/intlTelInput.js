/*
International Telephone Input v2.0.8
https://github.com/Bluefieldscom/intl-tel-input.git
*/
// wrap in UMD - see https://github.com/umdjs/umd/blob/master/jqueryPlugin.js
(function(factory) {
    if (typeof define === "function" && define.amd) {
        define([ "jquery" ], function($) {
            factory($, window, document);
        });
    } else {
        factory(jQuery, window, document);
    }
})(function($, window, document, undefined) {
    "use strict";
    var pluginName = "intlTelInput", id = 1, // give each instance it's own id for namespaced event handling
    defaults = {
        // automatically format the number according to the selected country
        autoFormat: true,
        // if there is just a dial code in the input: remove it on blur, and re-add it on focus
        autoHideDialCode: true,
        // default country
        defaultCountry: "",
        // don't insert international dial codes
        nationalMode: false,
        // display only these countries
        onlyCountries: [],
        // the countries at the top of the list. defaults to united states and united kingdom
        preferredCountries: [ "us", "gb" ],
        // make the dropdown the same width as the input
        responsiveDropdown: false,
        // specify the path to the libphonenumber script to enable validation
        validationScript: ""
    }, keys = {
        UP: 38,
        DOWN: 40,
        ENTER: 13,
        ESC: 27,
        PLUS: 43,
        A: 65,
        Z: 90,
        ZERO: 48,
        NINE: 57,
        SPACE: 32,
        BSPACE: 8,
        DEL: 46,
        CTRL: 17,
        CMD1: 91,
        // Chrome
        CMD2: 224
    }, windowLoaded = false;
    // keep track of if the window.load event has fired as impossible to check after the fact
    $(window).load(function() {
        windowLoaded = true;
    });
    function Plugin(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options);
        this._defaults = defaults;
        // event namespace
        this.ns = "." + pluginName + id++;
        // Chrome, FF, Safari, IE9+
        this.isGoodBrowser = Boolean(element.setSelectionRange);
        this._name = pluginName;
        this.init();
    }
    Plugin.prototype = {
        init: function() {
            // if in nationalMode, disable options relating to dial codes
            if (this.options.nationalMode) {
                this.options.autoFormat = this.options.autoHideDialCode = false;
            }
            // chrome on android has issues with key events
            // backspace issues for inputs with type=text: https://code.google.com/p/chromium/issues/detail?id=184812
            // and improper key codes for keyup and keydown: https://code.google.com/p/chromium/issues/detail?id=118639
            if (navigator.userAgent.match(/Android/i) && navigator.userAgent.match(/Chrome/i)) {
                this.options.autoFormat = false;
            }
            // process all the data: onlyCounties, preferredCountries, defaultCountry etc
            this._processCountryData();
            // generate the markup
            this._generateMarkup();
            // set the initial state of the input value and the selected flag
            this._setInitialState();
            // start all of the event listeners: autoHideDialCode, input keydown, selectedFlag click
            this._initListeners();
        },
        /********************
     *  PRIVATE METHODS
     ********************/
        // prepare all of the country data, including onlyCountries, preferredCountries and
        // defaultCountry options
        _processCountryData: function() {
            // set the instances country data objects
            this._setInstanceCountryData();
            // set the preferredCountries property
            this._setPreferredCountries();
        },
        // process onlyCountries array if present
        _setInstanceCountryData: function() {
            var that = this;
            if (this.options.onlyCountries.length) {
                var newCountries = [], newCountryCodes = {}, dialCode, i;
                for (i = 0; i < this.options.onlyCountries.length; i++) {
                    var countryCode = this.options.onlyCountries[i], countryData = that._getCountryData(countryCode, true, false);
                    if (countryData) {
                        newCountries.push(countryData);
                        // add this country's dial code to the countryCodes
                        dialCode = countryData.dialCode;
                        if (newCountryCodes[dialCode]) {
                            newCountryCodes[dialCode].push(countryCode);
                        } else {
                            newCountryCodes[dialCode] = [ countryCode ];
                        }
                    }
                }
                // maintain country priority
                for (dialCode in newCountryCodes) {
                    if (newCountryCodes[dialCode].length > 1) {
                        var sortedCountries = [];
                        // go through all of the allCountryCodes countries for this dialCode and create a new (ordered) array of values (if they're in the newCountryCodes array)
                        for (i = 0; i < allCountryCodes[dialCode].length; i++) {
                            var country = allCountryCodes[dialCode][i];
                            if ($.inArray(newCountryCodes[dialCode], country)) {
                                sortedCountries.push(country);
                            }
                        }
                        newCountryCodes[dialCode] = sortedCountries;
                    }
                }
                this.countries = newCountries;
                this.countryCodes = newCountryCodes;
            } else {
                this.countries = allCountries;
                this.countryCodes = allCountryCodes;
            }
        },
        // process preferred countries - iterate through the preferences,
        // fetching the country data for each one
        _setPreferredCountries: function() {
            var that = this;
            this.preferredCountries = [];
            for (var i = 0; i < this.options.preferredCountries.length; i++) {
                var countryCode = this.options.preferredCountries[i], countryData = that._getCountryData(countryCode, false, true);
                if (countryData) {
                    that.preferredCountries.push(countryData);
                }
            }
        },
        // generate all of the markup for the plugin: the selected flag overlay, and the dropdown
        _generateMarkup: function() {
            // telephone input
            this.telInput = $(this.element);
            // containers (mostly for positioning)
            this.telInput.wrap($("<div>", {
                "class": "intl-tel-input"
            }));
            var flagsContainer = $("<div>", {
                "class": "flag-dropdown"
            }).insertAfter(this.telInput);
            // currently selected flag (displayed to left of input)
            var selectedFlag = $("<div>", {
                "class": "selected-flag"
            }).appendTo(flagsContainer);
            this.selectedFlagInner = $("<div>", {
                "class": "flag"
            }).appendTo(selectedFlag);
            // CSS triangle
            $("<div>", {
                "class": "arrow"
            }).appendTo(this.selectedFlagInner);
            // country list contains: preferred countries, then divider, then all countries
            this.countryList = $("<ul>", {
                "class": "country-list v-hide"
            }).appendTo(flagsContainer);
            if (this.preferredCountries.length) {
                this._appendListItems(this.preferredCountries, "preferred");
                $("<li>", {
                    "class": "divider"
                }).appendTo(this.countryList);
            }
            this._appendListItems(this.countries, "");
            // now we can grab the dropdown height, and hide it properly
            this.dropdownHeight = this.countryList.outerHeight();
            this.countryList.removeClass("v-hide").addClass("hide");
            // and set the width
            if (this.options.responsiveDropdown) {
                this.countryList.outerWidth(this.telInput.outerWidth());
            }
            // this is useful in lots of places
            this.countryListItems = this.countryList.children(".country");
        },
        // add a country <li> to the countryList <ul> container
        _appendListItems: function(countries, className) {
            // we create so many DOM elements, I decided it was faster to build a temp string
            // and then add everything to the DOM in one go at the end
            var tmp = "";
            // for each country
            for (var i = 0; i < countries.length; i++) {
                var c = countries[i];
                // open the list item
                tmp += "<li class='country " + className + "' data-dial-code='" + c.dialCode + "' data-country-code='" + c.iso2 + "'>";
                // add the flag
                tmp += "<div class='flag " + c.iso2 + "'></div>";
                // and the country name and dial code
                tmp += "<span class='country-name'>" + c.name + "</span>";
                tmp += "<span class='dial-code'>+" + c.dialCode + "</span>";
                // close the list item
                tmp += "</li>";
            }
            this.countryList.append(tmp);
        },
        // set the initial state of the input value and the selected flag
        _setInitialState: function() {
            var val = this.telInput.val();
            // if the input is not pre-populated, or if it doesn't contain a valid dial code, fall back to the default country
            // Note: calling setNumber will also format the number
            if (!val || !this.setNumber(val)) {
                // flag is not set, so set to the default country
                var defaultCountry;
                // check the defaultCountry option, else fall back to the first in the list
                if (this.options.defaultCountry) {
                    defaultCountry = this._getCountryData(this.options.defaultCountry, false, false);
                } else {
                    defaultCountry = this.preferredCountries.length ? this.preferredCountries[0] : this.countries[0];
                }
                this._selectFlag(defaultCountry.iso2);
                // if autoHideDialCode is disabled, insert the default dial code
                if (!this.options.autoHideDialCode) {
                    this._resetToDialCode(defaultCountry.dialCode);
                }
            }
        },
        // initialise the main event listeners: input keydown, and click selected flag
        _initListeners: function() {
            var that = this;
            // auto hide dial code option
            if (this.options.autoHideDialCode) {
                this._initAutoHideDialCode();
            }
            // hack for input nested inside label: clicking the selected-flag to open the dropdown would then automatically trigger a 2nd click on the input which would close it again
            var label = this.telInput.closest("label");
            if (label.length) {
                label.on("click" + this.ns, function(e) {
                    // if the dropdown is closed, then focus the input, else ignore the click
                    if (that.countryList.hasClass("hide")) {
                        that.telInput.focus();
                    } else {
                        e.preventDefault();
                    }
                });
            }
            if (this.options.autoFormat) {
                // use keydown to prevent deleting the '+' prefix
                this.telInput.on("keydown" + this.ns, function(e) {
                    if ((e.which == keys.BSPACE || e.which == keys.DEL) && that.telInput.val() == "+") {
                        e.preventDefault();
                    }
                });
                // format number and update flag on keypress
                // use keypress event as we want to ignore all input except for a select few keys,
                // but we dont want to ignore the navigation keys like the arrows etc.
                // NOTE: no point in refactoring this to only bind these listeners on focus/blur because then you would need to have those 2 listeners running the whole time anyway...
                this.telInput.on("keypress" + this.ns, function(e) {
                    // 32 is space, and after that it's all chars (not meta/nav keys)
                    // this fix is needed for Firefox, which triggers keypress event for some meta/nav keys
                    if (e.which >= keys.SPACE) {
                        e.preventDefault();
                        // allowed keys are now just numeric keys
                        var isAllowed = e.which >= keys.ZERO && e.which <= keys.NINE, input = that.telInput[0], noSelection = that.isGoodBrowser && input.selectionStart == input.selectionEnd;
                        // still reformat even if not an allowed key as they could by typing a formatting char, but ignore if there's a selection as doesn't make sense to replace selection with illegal char and then immediately remove it
                        if (isAllowed || noSelection) {
                            var newChar = isAllowed ? String.fromCharCode(e.which) : null;
                            that._handleInputKey(newChar, false);
                        }
                    }
                });
            }
            // handle keyup event
            // for autoFormat: we use keyup to catch delete events after the fact
            this.telInput.on("keyup" + this.ns, function(e) {
                if (that.options.autoFormat) {
                    var isCtrl = e.which == keys.CTRL || e.which == keys.CMD1 || e.which == keys.CMD2, input = that.telInput[0], noSelection = that.isGoodBrowser && input.selectionStart == input.selectionEnd, cursorAtEnd = that.isGoodBrowser && input.selectionStart == that.telInput.val().length;
                    // if delete: format with suffix
                    // if backspace: format (if cursorAtEnd: no suffix)
                    // if ctrl and no selection (i.e. could be paste): format with suffix
                    if (e.which == keys.DEL || e.which == keys.BSPACE || isCtrl && noSelection) {
                        var preventFormatSuffix = e.which == keys.BSPACE && cursorAtEnd;
                        that._handleInputKey(null, preventFormatSuffix);
                    }
                    // if at the end the input is empty, then re-add the plus
                    if (!that.telInput.val()) {
                        that.telInput.val("+");
                    }
                } else {
                    // if no autoFormat, just update flag
                    that._updateFlag();
                }
            });
            // toggle country dropdown on click
            var selectedFlag = this.selectedFlagInner.parent();
            selectedFlag.on("click" + this.ns, function(e) {
                // only intercept this event if we're opening the dropdown
                // else let it bubble up to the top ("click-off-to-close" listener)
                // we cannot just stopPropagation as it may be needed to close another instance
                if (that.countryList.hasClass("hide") && !that.telInput.prop("disabled")) {
                    that._showDropdown();
                }
            });
            // if the user has specified the path to the validation script
            // inject a new script element for it at the end of the body
            if (this.options.validationScript) {
                var injectValidationScript = function() {
                    var script = document.createElement("script");
                    script.type = "text/javascript";
                    script.src = that.options.validationScript;
                    document.body.appendChild(script);
                };
                // if the plugin is being initialised after the window.load event has already been fired
                if (windowLoaded) {
                    injectValidationScript();
                } else {
                    // wait until the load event so we don't block any other requests e.g. the flags image
                    $(window).load(injectValidationScript);
                }
            }
        },
        // handle various key events on the input: the 2 main situations are 1) adding a new number character, which will replace any selection, reformat, and try to preserve the cursor position. and 2) reformatting on backspace, or paste event
        _handleInputKey: function(newNumericChar, preventFormatSuffix) {
            var val = this.telInput.val(), newCursor = null, cursorAtEnd = false, // raw DOM element
            input = this.telInput[0];
            if (this.isGoodBrowser) {
                var selectionEnd = input.selectionEnd, originalLen = val.length;
                cursorAtEnd = selectionEnd == originalLen;
                // if handling a new number character: insert it in the right place and calculate the new cursor position
                if (newNumericChar) {
                    // replace any selection they may have made with the new char
                    val = val.substring(0, input.selectionStart) + newNumericChar + val.substring(selectionEnd, originalLen);
                    // if the cursor was not at the end then calculate it's new pos
                    if (!cursorAtEnd) {
                        newCursor = selectionEnd + (val.length - originalLen);
                    }
                } else {
                    // here we're not handling a new char, we're just doing a re-format, but we still need to maintain the cursor position
                    newCursor = input.selectionStart;
                }
            } else if (newNumericChar) {
                val += newNumericChar;
            }
            // update the number and flag
            this.setNumber(val, preventFormatSuffix);
            // update the cursor position
            if (this.isGoodBrowser) {
                // if it was at the end, keep it there
                if (cursorAtEnd) {
                    newCursor = this.telInput.val().length;
                }
                input.setSelectionRange(newCursor, newCursor);
            }
        },
        // on focus: if empty add dial code. on blur: if just dial code, then empty it
        _initAutoHideDialCode: function() {
            var that = this;
            // mousedown decides where the cursor goes, so if we're focusing
            // we must prevent this from happening
            this.telInput.on("mousedown" + this.ns, function(e) {
                if (!that.telInput.is(":focus") && !that.telInput.val()) {
                    e.preventDefault();
                    // but this also cancels the focus, so we must trigger that manually
                    that._focus();
                }
            });
            // on focus: if empty, insert the dial code for the currently selected flag
            this.telInput.on("focus" + this.ns, function() {
                if (!that.telInput.val()) {
                    that._updateVal("+" + that.selectedCountryData.dialCode, true);
                    // after auto-inserting a dial code, if the first key they hit is '+' then assume
                    // they are entering a new number, so remove the dial code.
                    // use keypress instead of keydown because keydown gets triggered for the shift key
                    // (required to hit the + key), and instead of keyup because that shows the new '+'
                    // before removing the old one
                    that.telInput.one("keypress.plus" + that.ns, function(e) {
                        if (e.which == keys.PLUS) {
                            that.telInput.val("+");
                        }
                    });
                }
            });
            // on blur: if just a dial code then remove it
            this.telInput.on("blur" + this.ns, function() {
                var value = that.telInput.val(), startsPlus = value.substring(0, 1) == "+";
                if (startsPlus) {
                    var numeric = value.replace(/\D/g, ""), clean = "+" + numeric;
                    // if just a plus, or if just a dial code
                    if (!numeric || that.selectedCountryData.dialCode == numeric) {
                        that.telInput.val("");
                    }
                }
                // remove the keypress listener we added on focus
                that.telInput.off("keypress.plus" + that.ns);
            });
        },
        // focus input and put the cursor at the end
        _focus: function() {
            this.telInput.focus();
            var input = this.telInput[0];
            if (this.isGoodBrowser) {
                var len = this.telInput.val().length;
                input.setSelectionRange(len, len);
            }
        },
        // show the dropdown
        _showDropdown: function() {
            this._setDropdownPosition();
            // update highlighting and scroll to active list item
            var activeListItem = this.countryList.children(".active");
            this._highlightListItem(activeListItem);
            // show it
            this.countryList.removeClass("hide");
            this._scrollTo(activeListItem);
            // bind all the dropdown-related listeners: mouseover, click, click-off, keydown
            this._bindDropdownListeners();
            // update the arrow
            this.selectedFlagInner.children(".arrow").addClass("up");
        },
        // decide where to position dropdown (depends on position within viewport, and scroll)
        _setDropdownPosition: function() {
            var inputTop = this.telInput.offset().top, windowTop = $(window).scrollTop(), // dropdownFitsBelow = (dropdownBottom < windowBottom)
            dropdownFitsBelow = inputTop + this.telInput.outerHeight() + this.dropdownHeight < windowTop + $(window).height(), dropdownFitsAbove = inputTop - this.dropdownHeight > windowTop;
            // dropdownHeight - 1 for border
            var cssTop = !dropdownFitsBelow && dropdownFitsAbove ? "-" + (this.dropdownHeight - 1) + "px" : "";
            this.countryList.css("top", cssTop);
        },
        // we only bind dropdown listeners when the dropdown is open
        _bindDropdownListeners: function() {
            var that = this;
            // when mouse over a list item, just highlight that one
            // we add the class "highlight", so if they hit "enter" we know which one to select
            this.countryList.on("mouseover" + this.ns, ".country", function(e) {
                that._highlightListItem($(this));
            });
            // listen for country selection
            this.countryList.on("click" + this.ns, ".country", function(e) {
                that._selectListItem($(this));
            });
            // click off to close
            // (except when this initial opening click is bubbling up)
            // we cannot just stopPropagation as it may be needed to close another instance
            var isOpening = true;
            $("html").on("click" + this.ns, function(e) {
                if (!isOpening) {
                    that._closeDropdown();
                }
                isOpening = false;
            });
            // listen for up/down scrolling, enter to select, or letters to jump to country name.
            // use keydown as keypress doesn't fire for non-char keys and we want to catch if they
            // just hit down and hold it to scroll down (no keyup event).
            // listen on the document because that's where key events are triggered if no input has focus
            var query = "", queryTimer = null;
            $(document).on("keydown" + this.ns, function(e) {
                // prevent down key from scrolling the whole page,
                // and enter key from submitting a form etc
                e.preventDefault();
                if (e.which == keys.UP || e.which == keys.DOWN) {
                    // up and down to navigate
                    that._handleUpDownKey(e.which);
                } else if (e.which == keys.ENTER) {
                    // enter to select
                    that._handleEnterKey();
                } else if (e.which == keys.ESC) {
                    // esc to close
                    that._closeDropdown();
                } else if (e.which >= keys.A && e.which <= keys.Z || e.which == keys.SPACE) {
                    // upper case letters (note: keyup/keydown only return upper case letters)
                    // jump to countries that start with the query string
                    if (queryTimer) {
                        clearTimeout(queryTimer);
                    }
                    query += String.fromCharCode(e.which);
                    that._searchForCountry(query);
                    // if the timer hits 1 second, reset the query
                    queryTimer = setTimeout(function() {
                        query = "";
                    }, 1e3);
                }
            });
        },
        // highlight the next/prev item in the list (and ensure it is visible)
        _handleUpDownKey: function(key) {
            var current = this.countryList.children(".highlight").first();
            var next = key == keys.UP ? current.prev() : current.next();
            if (next.length) {
                // skip the divider
                if (next.hasClass("divider")) {
                    next = key == keys.UP ? next.prev() : next.next();
                }
                this._highlightListItem(next);
                this._scrollTo(next);
            }
        },
        // select the currently highlighted item
        _handleEnterKey: function() {
            var currentCountry = this.countryList.children(".highlight").first();
            if (currentCountry.length) {
                this._selectListItem(currentCountry);
            }
        },
        // find the first list item whose name starts with the query string
        _searchForCountry: function(query) {
            for (var i = 0; i < this.countries.length; i++) {
                if (this._startsWith(this.countries[i].name, query)) {
                    var listItem = this.countryList.children("[data-country-code=" + this.countries[i].iso2 + "]").not(".preferred");
                    // update highlighting and scroll
                    this._highlightListItem(listItem);
                    this._scrollTo(listItem, true);
                    break;
                }
            }
        },
        // check if (uppercase) string a starts with string b
        _startsWith: function(a, b) {
            return a.substr(0, b.length).toUpperCase() == b;
        },
        // update the input's value to the given val
        // if autoFormat=true, format it first according to the country-specific formatting rules
        _updateVal: function(val, hasDialCode, preventFormatSuffix) {
            var formatted = "", pure;
            if (this.options.autoFormat) {
                pure = val.replace(/\D/g, "");
                // only bother trying to format a number with a dialCode
                if (hasDialCode) {
                    // format the number
                    var format = this.selectedCountryData.format;
                    if (format) {
                        for (var i = 0; i < format.length; i++) {
                            // if the format character is a dot, add the number
                            if (format[i] == ".") {
                                // only break out of looping over the formatted chars when we need to insert another digit, but we cant
                                if (!pure) {
                                    break;
                                }
                                formatted += pure.substring(0, 1);
                                pure = pure.substring(1);
                                // in the case of a backspace event, stop at the last digit - dont add any extra formatting chars afterwards
                                if (!pure && preventFormatSuffix) {
                                    break;
                                }
                            } else {
                                formatted += format[i];
                            }
                        }
                    }
                }
                // if no formatted version, we're left with the "pure" numbers, so just make sure to preserve any initial '+'
                if (!formatted && val.substring(0, 1) == "+") {
                    formatted = "+";
                }
            } else {
                // no autoFormat, so just insert the true value
                pure = val;
            }
            this.telInput.val(formatted + pure);
        },
        // update the selected flag
        _updateFlag: function(number) {
            // try and extract valid dial code from input
            var dialCode = this._getDialCode(number);
            if (dialCode) {
                // check if one of the matching countries is already selected
                var countryCodes = this.countryCodes[dialCode.replace(/\D/g, "")], alreadySelected = false;
                // countries with area codes: we must always update the flag as if it's not an exact match
                // we should always default to the first country in the list. This is to avoid having to
                // explicitly define every possible area code in America (there are 999 possible area codes)
                if (!this.selectedCountryData || !this.selectedCountryData.hasAreaCodes) {
                    for (var i = 0; i < countryCodes.length; i++) {
                        if (this.selectedFlagInner.hasClass(countryCodes[i])) {
                            alreadySelected = true;
                        }
                    }
                }
                // else choose the first in the list
                if (!alreadySelected) {
                    this._selectFlag(countryCodes[0]);
                }
            }
            return dialCode;
        },
        // reset the input value to just a dial code
        _resetToDialCode: function(dialCode) {
            // if nationalMode is enabled then don't insert the dial code
            var value = this.options.nationalMode ? "" : "+" + dialCode;
            this.telInput.val(value);
        },
        // remove highlighting from other list items and highlight the given item
        _highlightListItem: function(listItem) {
            this.countryListItems.removeClass("highlight");
            listItem.addClass("highlight");
        },
        // find the country data for the given country code
        // the ignoreOnlyCountriesOption is only used during init() while parsing the onlyCountries array
        _getCountryData: function(countryCode, ignoreOnlyCountriesOption, allowFail) {
            var countryList = ignoreOnlyCountriesOption ? allCountries : this.countries;
            for (var i = 0; i < countryList.length; i++) {
                if (countryList[i].iso2 == countryCode) {
                    return countryList[i];
                }
            }
            if (allowFail) {
                return null;
            } else {
                throw new Error("No country data for '" + countryCode + "'");
            }
        },
        // update the selected flag and the active list item
        _selectFlag: function(countryCode) {
            this.selectedFlagInner.attr("class", "flag " + countryCode);
            // update the title attribute
            this.selectedCountryData = this._getCountryData(countryCode, false, false);
            var title = this.selectedCountryData.name + ": +" + this.selectedCountryData.dialCode;
            this.selectedFlagInner.parent().attr("title", title);
            // update the active list item
            var listItem = this.countryListItems.children(".flag." + countryCode).first().parent();
            this.countryListItems.removeClass("active");
            listItem.addClass("active");
        },
        // called when the user selects a list item from the dropdown
        _selectListItem: function(listItem) {
            // update selected flag and active list item
            var countryCode = listItem.attr("data-country-code");
            this._selectFlag(countryCode);
            this._closeDropdown();
            // update input value
            if (!this.options.nationalMode) {
                this._updateDialCode("+" + listItem.attr("data-dial-code"));
                this.telInput.trigger("change");
            }
            // focus the input
            this._focus();
        },
        // close the dropdown and unbind any listeners
        _closeDropdown: function() {
            this.countryList.addClass("hide");
            // update the arrow
            this.selectedFlagInner.children(".arrow").removeClass("up");
            // unbind key events
            $(document).off(this.ns);
            // unbind click-off-to-close
            $("html").off(this.ns);
            // unbind hover and click listeners
            this.countryList.off(this.ns);
        },
        // check if an element is visible within it's container, else scroll until it is
        _scrollTo: function(element, middle) {
            var container = this.countryList, containerHeight = container.height(), containerTop = container.offset().top, containerBottom = containerTop + containerHeight, elementHeight = element.outerHeight(), elementTop = element.offset().top, elementBottom = elementTop + elementHeight, newScrollTop = elementTop - containerTop + container.scrollTop(), middleOffset = containerHeight / 2 - elementHeight / 2;
            if (elementTop < containerTop) {
                // scroll up
                if (middle) {
                    newScrollTop -= middleOffset;
                }
                container.scrollTop(newScrollTop);
            } else if (elementBottom > containerBottom) {
                // scroll down
                if (middle) {
                    newScrollTop += middleOffset;
                }
                var heightDifference = containerHeight - elementHeight;
                container.scrollTop(newScrollTop - heightDifference);
            }
        },
        // replace any existing dial code with the new one
        _updateDialCode: function(newDialCode) {
            var inputVal = this.telInput.val(), prevDialCode = this._getDialCode(), newNumber;
            // if the previous number contained a valid dial code, replace it
            // (if more than just a plus character)
            if (prevDialCode.length > 1) {
                newNumber = inputVal.replace(prevDialCode, newDialCode);
            } else {
                // if the previous number didn't contain a dial code, we should persist it
                var existingNumber = inputVal && inputVal.substr(0, 1) != "+" ? $.trim(inputVal) : "";
                newNumber = newDialCode + existingNumber;
            }
            this._updateVal(newNumber, true);
        },
        // try and extract a valid international dial code from a full telephone number
        // Note: returns the raw string inc plus character and any whitespace/dots etc
        _getDialCode: function(number) {
            var dialCode = "", inputVal = number || this.telInput.val();
            // only interested in international numbers (starting with a plus)
            if (inputVal.charAt(0) == "+") {
                var numericChars = "";
                // iterate over chars
                for (var i = 0; i < inputVal.length; i++) {
                    var c = inputVal.charAt(i);
                    // if char is number
                    if ($.isNumeric(c)) {
                        numericChars += c;
                        // if current numericChars make a valid dial code
                        if (this.countryCodes[numericChars]) {
                            // store the actual raw string (useful for matching later)
                            dialCode = inputVal.substring(0, i + 1);
                        }
                        // longest dial code is 4 chars
                        if (numericChars.length == 4) {
                            break;
                        }
                    }
                }
            }
            return dialCode;
        },
        /********************
     *  PUBLIC METHODS
     ********************/
        // remove plugin
        destroy: function() {
            // make sure the dropdown is closed (and unbind listeners)
            this._closeDropdown();
            // key events, and focus/blur events if autoHideDialCode=true
            this.telInput.off(this.ns);
            // click event to open dropdown
            this.selectedFlagInner.parent().off(this.ns);
            // label click hack
            this.telInput.closest("label").off(this.ns);
            // remove markup
            var container = this.telInput.parent();
            container.before(this.telInput).remove();
        },
        // get the country data for the currently selected flag
        getSelectedCountryData: function() {
            return this.selectedCountryData;
        },
        // validate the input val - assumes the global function isValidNumber
        // pass in true if you want to allow national numbers (no country dial code)
        isValidNumber: function(allowNational) {
            var val = $.trim(this.telInput.val()), countryCode = allowNational ? this.selectedCountryData.iso2 : "", // libphonenumber allows alpha chars, but in order to allow that, we'd need a method to retrieve the processed number, with letters replaced with numbers
            containsAlpha = /[a-zA-Z]/.test(val);
            return !containsAlpha && window.isValidNumber(val, countryCode);
        },
        // update the selected flag, and if the input is empty: insert the new dial code
        selectCountry: function(countryCode) {
            // check if already selected
            if (!this.selectedFlagInner.hasClass(countryCode)) {
                this._selectFlag(countryCode);
                if (!this.telInput.val() && !this.options.autoHideDialCode) {
                    this._resetToDialCode(this.selectedCountryData.dialCode);
                }
            }
        },
        // set the input value and update the flag
        setNumber: function(number, preventFormatSuffix) {
            // we must update the flag first, which updates this.selectedCountryData, which is used later for formatting the number before displaying it
            var dialCode = this._updateFlag(number);
            this._updateVal(number, dialCode, preventFormatSuffix);
            return dialCode;
        }
    };
    // adapted to allow public functions
    // using https://github.com/jquery-boilerplate/jquery-boilerplate/wiki/Extending-jQuery-Boilerplate
    $.fn[pluginName] = function(options) {
        var args = arguments;
        // Is the first parameter an object (options), or was omitted,
        // instantiate a new instance of the plugin.
        if (options === undefined || typeof options === "object") {
            return this.each(function() {
                if (!$.data(this, "plugin_" + pluginName)) {
                    $.data(this, "plugin_" + pluginName, new Plugin(this, options));
                }
            });
        } else if (typeof options === "string" && options[0] !== "_" && options !== "init") {
            // If the first parameter is a string and it doesn't start
            // with an underscore or "contains" the `init`-function,
            // treat this as a call to a public method.
            // Cache the method call to make it possible to return a value
            var returns;
            this.each(function() {
                var instance = $.data(this, "plugin_" + pluginName);
                // Tests that there's already a plugin-instance
                // and checks that the requested public method exists
                if (instance instanceof Plugin && typeof instance[options] === "function") {
                    // Call the method of our plugin instance,
                    // and pass it the supplied arguments.
                    returns = instance[options].apply(instance, Array.prototype.slice.call(args, 1));
                }
                // Allow instances to be destroyed via the 'destroy' method
                if (options === "destroy") {
                    $.data(this, "plugin_" + pluginName, null);
                }
            });
            // If the earlier cached method gives a value back return the value,
            // otherwise return this to preserve chainability.
            return returns !== undefined ? returns : this;
        }
    };
    /********************
   *  STATIC METHODS
   ********************/
    // get the country data object
    $.fn[pluginName].getCountryData = function() {
        return allCountries;
    };
    // set the country data object
    $.fn[pluginName].setCountryData = function(obj) {
        allCountries = obj;
    };
    // Tell JSHint to ignore this warning: "character may get silently deleted by one or more browsers"
    // jshint -W100
    // Array of country objects for the flag dropdown.
    // Each contains a name, country code (ISO 3166-1 alpha-2) and dial code.
    // Originally from https://github.com/mledoze/countries
    // then modified using the following JavaScript (NOW OUT OF DATE):
    /*
var result = [];
_.each(countries, function(c) {
  // ignore countries without a dial code
  if (c.callingCode[0].length) {
    result.push({
      // var locals contains country names with localised versions in brackets
      n: _.findWhere(locals, {
        countryCode: c.cca2
      }).name,
      i: c.cca2.toLowerCase(),
      d: c.callingCode[0]
    });
  }
});
JSON.stringify(result);
*/
    // then with a couple of manual re-arrangements to be alphabetical
    // then changed Kazakhstan from +76 to +7
    // and Vatican City from +379 to +39 (see issue 50)
    // and Caribean Netherlands from +5997 to +599
    // and Curacao from +5999 to +599
    // Removed: Ã…land Islands, Christmas Island, Cocos Islands, Guernsey, Isle of Man, Jersey, Kosovo, Mayotte, Pitcairn Islands, South Georgia, Svalbard, Western Sahara
    // Update: converted objects to arrays to save bytes!
    // Update: added formats for some countries
    // Update: added "priority" for countries with the same dialCode as others
    // Update: added array of area codes for countries with the same dialCode as others
    // So each country array has the following information:
    // [
    //    Country name,
    //    iso2 code,
    //    International dial code,
    //    Format (if available),
    //    Order (if >1 country with same dial code),
    //    Area codes (if >1 country with same dial code)
    // ]
    var allCountries = [ [ "Afghanistan (â€«Ø§ÙØºØ§Ù†Ø³ØªØ§Ù†â€¬â€Ž)", "af", "93" ], [ "Albania (ShqipÃ«ri)", "al", "355" ], [ "Algeria (â€«Ø§Ù„Ø¬Ø²Ø§Ø¦Ø±â€¬â€Ž)", "dz", "213" ], [ "American Samoa", "as", "1684" ], [ "Andorra", "ad", "376" ], [ "Angola", "ao", "244" ], [ "Anguilla", "ai", "1264" ], [ "Antigua and Barbuda", "ag", "1268" ], [ "Argentina", "ar", "54" ], [ "Armenia (Õ€Õ¡ÕµÕ¡Õ½Õ¿Õ¡Õ¶)", "am", "374" ], [ "Aruba", "aw", "297" ], [ "Australia", "au", "61", "+.. ... ... ..." ], [ "Austria (Ã–sterreich)", "at", "43" ], [ "Azerbaijan (AzÉ™rbaycan)", "az", "994" ], [ "Bahamas", "bs", "1242" ], [ "Bahrain (â€«Ø§Ù„Ø¨Ø­Ø±ÙŠÙ†â€¬â€Ž)", "bh", "973" ], [ "Bangladesh (à¦¬à¦¾à¦‚à¦²à¦¾à¦¦à§‡à¦¶)", "bd", "880" ], [ "Barbados", "bb", "1246" ], [ "Belarus (Ð‘ÐµÐ»Ð°Ñ€ÑƒÑÑŒ)", "by", "375" ], [ "Belgium (BelgiÃ«)", "be", "32", "+.. ... .. .. .." ], [ "Belize", "bz", "501" ], [ "Benin (BÃ©nin)", "bj", "229" ], [ "Bermuda", "bm", "1441" ], [ "Bhutan (à½ à½–à¾²à½´à½‚)", "bt", "975" ], [ "Bolivia", "bo", "591" ], [ "Bosnia and Herzegovina (Ð‘Ð¾ÑÐ½Ð° Ð¸ Ð¥ÐµÑ€Ñ†ÐµÐ³Ð¾Ð²Ð¸Ð½Ð°)", "ba", "387" ], [ "Botswana", "bw", "267" ], [ "Brazil (Brasil)", "br", "55" ], [ "British Indian Ocean Territory", "io", "246" ], [ "British Virgin Islands", "vg", "1284" ], [ "Brunei", "bn", "673" ], [ "Bulgaria (Ð‘ÑŠÐ»Ð³Ð°Ñ€Ð¸Ñ)", "bg", "359" ], [ "Burkina Faso", "bf", "226" ], [ "Burundi (Uburundi)", "bi", "257" ], [ "Cambodia (áž€áž˜áŸ’áž–áž»áž‡áž¶)", "kh", "855" ], [ "Cameroon (Cameroun)", "cm", "237" ], [ "Canada", "ca", "1", "+. (...) ...-....", 1, [ "204", "236", "249", "250", "289", "306", "343", "365", "387", "403", "416", "418", "431", "437", "438", "450", "506", "514", "519", "548", "579", "581", "587", "604", "613", "639", "647", "672", "705", "709", "742", "778", "780", "782", "807", "819", "825", "867", "873", "902", "905" ] ], [ "Cape Verde (Kabu Verdi)", "cv", "238" ], [ "Caribbean Netherlands", "bq", "599", "", 1 ], [ "Cayman Islands", "ky", "1345" ], [ "Central African Republic (RÃ©publique centrafricaine)", "cf", "236" ], [ "Chad (Tchad)", "td", "235" ], [ "Chile", "cl", "56" ], [ "China (ä¸­å›½)", "cn", "86", "+.. ..-........" ], [ "Colombia", "co", "57" ], [ "Comoros (â€«Ø¬Ø²Ø± Ø§Ù„Ù‚Ù…Ø±â€¬â€Ž)", "km", "269" ], [ "Congo (DRC) (Jamhuri ya Kidemokrasia ya Kongo)", "cd", "243" ], [ "Congo (Republic) (Congo-Brazzaville)", "cg", "242" ], [ "Cook Islands", "ck", "682" ], [ "Costa Rica", "cr", "506", "+... ....-...." ], [ "CÃ´te dâ€™Ivoire", "ci", "225" ], [ "Croatia (Hrvatska)", "hr", "385" ], [ "Cuba", "cu", "53" ], [ "CuraÃ§ao", "cw", "599", "", 0 ], [ "Cyprus (ÎšÏÏ€ÏÎ¿Ï‚)", "cy", "357" ], [ "Czech Republic (ÄŒeskÃ¡ republika)", "cz", "420" ], [ "Denmark (Danmark)", "dk", "45", "+.. .. .. .. .." ], [ "Djibouti", "dj", "253" ], [ "Dominica", "dm", "1767" ], [ "Dominican Republic (RepÃºblica Dominicana)", "do", "1", "", 2, [ "809", "829", "849" ] ], [ "Ecuador", "ec", "593" ], [ "Egypt (â€«Ù…ØµØ±â€¬â€Ž)", "eg", "20" ], [ "El Salvador", "sv", "503", "+... ....-...." ], [ "Equatorial Guinea (Guinea Ecuatorial)", "gq", "240" ], [ "Eritrea", "er", "291" ], [ "Estonia (Eesti)", "ee", "372" ], [ "Ethiopia", "et", "251" ], [ "Falkland Islands (Islas Malvinas)", "fk", "500" ], [ "Faroe Islands (FÃ¸royar)", "fo", "298" ], [ "Fiji", "fj", "679" ], [ "Finland (Suomi)", "fi", "358", "+... .. ... .. .." ], [ "France", "fr", "33", "+.. . .. .. .. .." ], [ "French Guiana (Guyane franÃ§aise)", "gf", "594" ], [ "French Polynesia (PolynÃ©sie franÃ§aise)", "pf", "689" ], [ "Gabon", "ga", "241" ], [ "Gambia", "gm", "220" ], [ "Georgia (áƒ¡áƒáƒ¥áƒáƒ áƒ—áƒ•áƒ”áƒšáƒ)", "ge", "995" ], [ "Germany (Deutschland)", "de", "49", "+.. ... ......." ], [ "Ghana (Gaana)", "gh", "233" ], [ "Gibraltar", "gi", "350" ], [ "Greece (Î•Î»Î»Î¬Î´Î±)", "gr", "30" ], [ "Greenland (Kalaallit Nunaat)", "gl", "299" ], [ "Grenada", "gd", "1473" ], [ "Guadeloupe", "gp", "590", "", 0 ], [ "Guam", "gu", "1671" ], [ "Guatemala", "gt", "502", "+... ....-...." ], [ "Guinea (GuinÃ©e)", "gn", "224" ], [ "Guinea-Bissau (GuinÃ© Bissau)", "gw", "245" ], [ "Guyana", "gy", "592" ], [ "Haiti", "ht", "509", "+... ....-...." ], [ "Honduras", "hn", "504" ], [ "Hong Kong (é¦™æ¸¯)", "hk", "852", "+... .... ...." ], [ "Hungary (MagyarorszÃ¡g)", "hu", "36" ], [ "Iceland (Ãsland)", "is", "354", "+... ... ...." ], [ "India (à¤­à¤¾à¤°à¤¤)", "in", "91", "+.. .....-....." ], [ "Indonesia", "id", "62" ], [ "Iran (â€«Ø§ÛŒØ±Ø§Ù†â€¬â€Ž)", "ir", "98" ], [ "Iraq (â€«Ø§Ù„Ø¹Ø±Ø§Ù‚â€¬â€Ž)", "iq", "964" ], [ "Ireland", "ie", "353", "+... .. ......." ], [ "Israel (â€«×™×©×¨××œâ€¬â€Ž)", "il", "972" ], [ "Italy (Italia)", "it", "39", "+.. ... ......", 0 ], [ "Jamaica", "jm", "1876" ], [ "Japan (æ—¥æœ¬)", "jp", "81", "+.. ... .. ...." ], [ "Jordan (â€«Ø§Ù„Ø£Ø±Ø¯Ù†â€¬â€Ž)", "jo", "962" ], [ "Kazakhstan (ÐšÐ°Ð·Ð°Ñ…ÑÑ‚Ð°Ð½)", "kz", "7", "+. ... ...-..-..", 1 ], [ "Kenya", "ke", "254" ], [ "Kiribati", "ki", "686" ], [ "Kuwait (â€«Ø§Ù„ÙƒÙˆÙŠØªâ€¬â€Ž)", "kw", "965" ], [ "Kyrgyzstan (ÐšÑ‹Ñ€Ð³Ñ‹Ð·ÑÑ‚Ð°Ð½)", "kg", "996" ], [ "Laos (àº¥àº²àº§)", "la", "856" ], [ "Latvia (Latvija)", "lv", "371" ], [ "Lebanon (â€«Ù„Ø¨Ù†Ø§Ù†â€¬â€Ž)", "lb", "961" ], [ "Lesotho", "ls", "266" ], [ "Liberia", "lr", "231" ], [ "Libya (â€«Ù„ÙŠØ¨ÙŠØ§â€¬â€Ž)", "ly", "218" ], [ "Liechtenstein", "li", "423" ], [ "Lithuania (Lietuva)", "lt", "370" ], [ "Luxembourg", "lu", "352" ], [ "Macau (æ¾³é–€)", "mo", "853" ], [ "Macedonia (FYROM) (ÐœÐ°ÐºÐµÐ´Ð¾Ð½Ð¸Ñ˜Ð°)", "mk", "389" ], [ "Madagascar (Madagasikara)", "mg", "261" ], [ "Malawi", "mw", "265" ], [ "Malaysia", "my", "60", "+.. ..-....-...." ], [ "Maldives", "mv", "960" ], [ "Mali", "ml", "223" ], [ "Malta", "mt", "356" ], [ "Marshall Islands", "mh", "692" ], [ "Martinique", "mq", "596" ], [ "Mauritania (â€«Ù…ÙˆØ±ÙŠØªØ§Ù†ÙŠØ§â€¬â€Ž)", "mr", "222" ], [ "Mauritius (Moris)", "mu", "230" ], [ "Mexico (MÃ©xico)", "mx", "52" ], [ "Micronesia", "fm", "691" ], [ "Moldova (Republica Moldova)", "md", "373" ], [ "Monaco", "mc", "377" ], [ "Mongolia (ÐœÐ¾Ð½Ð³Ð¾Ð»)", "mn", "976" ], [ "Montenegro (Crna Gora)", "me", "382" ], [ "Montserrat", "ms", "1664" ], [ "Morocco (â€«Ø§Ù„Ù…ØºØ±Ø¨â€¬â€Ž)", "ma", "212" ], [ "Mozambique (MoÃ§ambique)", "mz", "258" ], [ "Myanmar (Burma) (á€™á€¼á€”á€ºá€™á€¬)", "mm", "95" ], [ "Namibia (NamibiÃ«)", "na", "264" ], [ "Nauru", "nr", "674" ], [ "Nepal (à¤¨à¥‡à¤ªà¤¾à¤²)", "np", "977" ], [ "Netherlands (Nederland)", "nl", "31", "+.. .. ........" ], [ "New Caledonia (Nouvelle-CalÃ©donie)", "nc", "687" ], [ "New Zealand", "nz", "64", "+.. ...-...-...." ], [ "Nicaragua", "ni", "505" ], [ "Niger (Nijar)", "ne", "227" ], [ "Nigeria", "ng", "234" ], [ "Niue", "nu", "683" ], [ "Norfolk Island", "nf", "672" ], [ "North Korea (ì¡°ì„  ë¯¼ì£¼ì£¼ì˜ ì¸ë¯¼ ê³µí™”êµ­)", "kp", "850" ], [ "Northern Mariana Islands", "mp", "1670" ], [ "Norway (Norge)", "no", "47", "+.. ... .. ..." ], [ "Oman (â€«Ø¹ÙÙ…Ø§Ù†â€¬â€Ž)", "om", "968" ], [ "Pakistan (â€«Ù¾Ø§Ú©Ø³ØªØ§Ù†â€¬â€Ž)", "pk", "92", "+.. ...-......." ], [ "Palau", "pw", "680" ], [ "Palestine (â€«ÙÙ„Ø³Ø·ÙŠÙ†â€¬â€Ž)", "ps", "970" ], [ "Panama (PanamÃ¡)", "pa", "507" ], [ "Papua New Guinea", "pg", "675" ], [ "Paraguay", "py", "595" ], [ "Peru (PerÃº)", "pe", "51" ], [ "Philippines", "ph", "63", "+.. ... ...." ], [ "Poland (Polska)", "pl", "48", "+.. ...-...-..." ], [ "Portugal", "pt", "351" ], [ "Puerto Rico", "pr", "1", "", 3, [ "787", "939" ] ], [ "Qatar (â€«Ù‚Ø·Ø±â€¬â€Ž)", "qa", "974" ], [ "RÃ©union (La RÃ©union)", "re", "262" ], [ "Romania (RomÃ¢nia)", "ro", "40" ], [ "Russia (Ð Ð¾ÑÑÐ¸Ñ)", "ru", "7", "+. ... ...-..-..", 0 ], [ "Rwanda", "rw", "250" ], [ "Saint BarthÃ©lemy (Saint-BarthÃ©lemy)", "bl", "590", "", 1 ], [ "Saint Helena", "sh", "290" ], [ "Saint Kitts and Nevis", "kn", "1869" ], [ "Saint Lucia", "lc", "1758" ], [ "Saint Martin (Saint-Martin (partie franÃ§aise))", "mf", "590", "", 2 ], [ "Saint Pierre and Miquelon (Saint-Pierre-et-Miquelon)", "pm", "508" ], [ "Saint Vincent and the Grenadines", "vc", "1784" ], [ "Samoa", "ws", "685" ], [ "San Marino", "sm", "378" ], [ "SÃ£o TomÃ© and PrÃ­ncipe (SÃ£o TomÃ© e PrÃ­ncipe)", "st", "239" ], [ "Saudi Arabia (â€«Ø§Ù„Ù…Ù…Ù„ÙƒØ© Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© Ø§Ù„Ø³Ø¹ÙˆØ¯ÙŠØ©â€¬â€Ž)", "sa", "966" ], [ "Senegal (SÃ©nÃ©gal)", "sn", "221" ], [ "Serbia (Ð¡Ñ€Ð±Ð¸Ñ˜Ð°)", "rs", "381" ], [ "Seychelles", "sc", "248" ], [ "Sierra Leone", "sl", "232" ], [ "Singapore", "sg", "65", "+.. ....-...." ], [ "Sint Maarten", "sx", "1721" ], [ "Slovakia (Slovensko)", "sk", "421" ], [ "Slovenia (Slovenija)", "si", "386" ], [ "Solomon Islands", "sb", "677" ], [ "Somalia (Soomaaliya)", "so", "252" ], [ "South Africa", "za", "27" ], [ "South Korea (ëŒ€í•œë¯¼êµ­)", "kr", "82" ], [ "South Sudan (â€«Ø¬Ù†ÙˆØ¨ Ø§Ù„Ø³ÙˆØ¯Ø§Ù†â€¬â€Ž)", "ss", "211" ], [ "Spain (EspaÃ±a)", "es", "34", "+.. ... ... ..." ], [ "Sri Lanka (à·à·Šâ€à¶»à·“ à¶½à¶‚à¶šà·à·€)", "lk", "94" ], [ "Sudan (â€«Ø§Ù„Ø³ÙˆØ¯Ø§Ù†â€¬â€Ž)", "sd", "249" ], [ "Suriname", "sr", "597" ], [ "Swaziland", "sz", "268" ], [ "Sweden (Sverige)", "se", "46" ], [ "Switzerland (Schweiz)", "ch", "41", "+.. .. ... .. .." ], [ "Syria (â€«Ø³ÙˆØ±ÙŠØ§â€¬â€Ž)", "sy", "963" ], [ "Taiwan (å°ç£)", "tw", "886" ], [ "Tajikistan", "tj", "992" ], [ "Tanzania", "tz", "255" ], [ "Thailand (à¹„à¸—à¸¢)", "th", "66" ], [ "Timor-Leste", "tl", "670" ], [ "Togo", "tg", "228" ], [ "Tokelau", "tk", "690" ], [ "Tonga", "to", "676" ], [ "Trinidad and Tobago", "tt", "1868" ], [ "Tunisia (â€«ØªÙˆÙ†Ø³â€¬â€Ž)", "tn", "216" ], [ "Turkey (TÃ¼rkiye)", "tr", "90", "+.. ... ... .. .." ], [ "Turkmenistan", "tm", "993" ], [ "Turks and Caicos Islands", "tc", "1649" ], [ "Tuvalu", "tv", "688" ], [ "U.S. Virgin Islands", "vi", "1340" ], [ "Uganda", "ug", "256" ], [ "Ukraine (Ð£ÐºÑ€Ð°Ñ—Ð½Ð°)", "ua", "380" ], [ "United Arab Emirates (â€«Ø§Ù„Ø¥Ù…Ø§Ø±Ø§Øª Ø§Ù„Ø¹Ø±Ø¨ÙŠØ© Ø§Ù„Ù…ØªØ­Ø¯Ø©â€¬â€Ž)", "ae", "971" ], [ "United Kingdom", "gb", "44", "+.. .... ......" ], [ "United States", "us", "1", "+. (...) ...-....", 0 ], [ "Uruguay", "uy", "598" ], [ "Uzbekistan (OÊ»zbekiston)", "uz", "998" ], [ "Vanuatu", "vu", "678" ], [ "Vatican City (CittÃ  del Vaticano)", "va", "39", "+.. .. .... ....", 1 ], [ "Venezuela", "ve", "58" ], [ "Vietnam (Viá»‡t Nam)", "vn", "84" ], [ "Wallis and Futuna", "wf", "681" ], [ "Yemen (â€«Ø§Ù„ÙŠÙ…Ù†â€¬â€Ž)", "ye", "967" ], [ "Zambia", "zm", "260" ], [ "Zimbabwe", "zw", "263" ] ];
    // we will build this in the loop below
    var allCountryCodes = {};
    var addCountryCode = function(iso2, dialCode, priority) {
        if (!(dialCode in allCountryCodes)) {
            allCountryCodes[dialCode] = [];
        }
        var index = priority || 0;
        allCountryCodes[dialCode][index] = iso2;
    };
    // loop over all of the countries above
    for (var i = 0; i < allCountries.length; i++) {
        // countries
        var c = allCountries[i];
        allCountries[i] = {
            name: c[0],
            iso2: c[1],
            dialCode: c[2]
        };
        // format
        if (c[3]) {
            allCountries[i].format = c[3];
        }
        // area codes
        if (c[5]) {
            allCountries[i].hasAreaCodes = true;
            for (var j = 0; j < c[5].length; j++) {
                // full dial code is country code + dial code
                var dialCode = c[2] + c[5][j];
                addCountryCode(c[1], dialCode);
            }
        }
        // dial codes
        addCountryCode(c[1], c[2], c[4]);
    }
});