odoo.define('wt_customization.countdown', function (require) {
"use strict";

var fieldRegistry = require('web.field_registry');
var AbstractField = require('web.AbstractField');
var FormView = require('web.FormView');
var session = require('web.session');

var TimerFieldWidget = AbstractField.extend({

    /**
     * @override
     * @private
     */
    _render: function () {
        debugger
        this._super.apply(this, arguments);
    },

});
fieldRegistry.add('timer_start_field', TimerFieldWidget);
});
