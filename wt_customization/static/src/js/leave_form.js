odoo.define("wt_custom_host_partner.leave_form", function(require){  
    "use strict";
    // debugger
    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const core = require('web.core');
    var _t = core._t;

    publicWidget.registry.Leaveform = publicWidget.Widget.extend({
        selector:'#wrap',
        events: {
            "change input[name='is_halfday']": '_Onchange_fields',
            "change input[name='date_from']":'_Get_Duration',
            "change input[name='date_to']":'_Get_Duration',
        },
        _Onchange_fields: function (ev) {
            if ($('#is_halfday').prop('checked') === true){
                $('.from_date').removeAttr("required")
                $('.from_date').addClass('d-none')
                document.getElementById("duration").value = 0.5
            }
            if ($('#is_halfday').prop('checked') === false){
                $('.from_date').attr("required", "true")
                $('.from_date').removeClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === true){
                $('.to_date').removeAttr("required")
                $('.to_date').addClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === false){
                $('.to_date').attr("required", "true")
                $('.to_date').removeClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === true){
                $('.halfdaydate').attr("required", "true")
                $('.halfdaydate').removeClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === false){
                $('.halfdaydate').removeAttr("required")
                $('.halfdaydate').addClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === true){
                $('.date_period').attr("required", "true")
                $('.date_period').removeClass('d-none')
            }
            if ($('#is_halfday').prop('checked') === false){
                $('.date_period').removeAttr("required")
                $('.date_period').addClass('d-none')
                document.getElementById("duration").value = this._Get_Duration()
            }
    },
    _Get_Duration:function(ev){
        const startDate = document.getElementById("date_from").value
        const endDate = document.getElementById("date_to").value
        if (startDate && endDate){
            debugger
            const strt = new Date(startDate)
            const end = new Date(endDate)
            if (end < strt){
                Dialog.alert(this, _t("You have selected the wrong date. Please check it or enter the date again."));
            }

            let duration = end - strt;
            let f_duration = Math.floor(duration / (24 * 60 * 60 * 1000));
            document.getElementById("duration").value = f_duration + 1
        }
    },
    })
})