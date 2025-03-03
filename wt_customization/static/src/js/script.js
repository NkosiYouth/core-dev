odoo.define("wt_custom_host_partner.host_site_recruitment", function(require){
    "use strict";
    var core = require('web.core');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    const dom = require('web.dom');

    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.HostSiteRecruitment = publicWidget.Widget.extend({
        selector:'#wrap',
        events: {
            'click #host_site_partner_submit':'_submit',
            'click #host_site_partner_add': 'host_site_partner_add',
            'click #host_site_partner_remove': 'host_site_partner_remove',
            'input input[name="company_type"]':"_company_input",
            "change select[name='country_id']": '_get_state',
        },
        init() {
            this._super(...arguments);
            this.__started = new Promise(resolve => this.__startResolve = resolve);
        },
        /**
         * @override
         */
        start(){
            this._super.apply(this, arguments);
            this.form_count = 0;
            this.country_state();
        }, 
        _prevent_default_radio(ev){
            ev.preventDefault();
        },
        async _get_state(ev){
            if(this.form_count > 0 && ev.target.dataset.changeId){
                let form_val = ev.target.dataset.changeId;
                const country_id = ev.target.value;
                await ajax.jsonRpc("/get_states","call",{country_id:parseInt(country_id)})
                .then((res)=>{
                    const form = document.getElementById(`host_partener_main_form_${form_val}`);
                    const country_state = form.querySelector("select[name='state_id']");
                    const options = country_state.options;
                    const size = country_state.options.length;
                    for(let i=size-1; i>=0; i--){
                        country_state.options.remove(options[i]);
                    } 
                    $.each(res, function(index, state){
                        const option = document.createElement('option');
                        option.text = state.name;
                        option.value = state.id;
                        country_state.appendChild(option);
                    });
                })
            }else{
                this.country_state();
            }
        },
        async country_state(){
            const country = $("select[name='country_id']")
            if(country[0]){
                const country_id = country.val();

                await ajax.jsonRpc("/get_states","call",{country_id:parseInt(country_id)})
               .then((res)=>{
                    const country_state = $("select[name='state_id']")[0];
                    const options = country_state.options;
                    const size = country_state.options.length;
                    for(let i=size-1; i>=0; i--){
                        country_state.options.remove(options[i]);
                    } 
                    $.each(res, function(index, state){
                        const option = document.createElement('option');
                        option.text = state.name;
                        option.value = state.id;
                        country_state.appendChild(option);
                    });
                })
            }
        }, 
        _company_input(ev){
            const selctionDiv = $('.company_type_selection')[0];
            if(ev.target.value === "Partner"){
                const h5 = document.createElement('h5');
                h5.textContent = "As a partner you will add host sites below.";
                h5.classList.add("text-danger", "text-center", "host_site_required");
                selctionDiv.appendChild(h5);
                $('#host_site_partner_add')[0].classList.remove('d-none');
                $('#host_site_partner_remove')[0].classList.remove('d-none');
            }else{
                if($('.host_site_required')){
                    $('.host_site_required').remove(); 
                }
                $('#host_site_partner_add')[0].classList.add('d-none');
                $('#host_site_partner_remove')[0].classList.add('d-none');
                this.reset_forms()
            }
        },
        reset_forms(){
            const container = document.querySelector("#host_partner_container");
            for(let i=1; i <= this.form_count; i++){
                container.removeChild(document.getElementById(`host_partener_main_form_${i}`));
            }
            this.form_count = 0;
        },
       async host_site_partner_add(){
            this.form_count++;
            const container = document.querySelector("#host_partner_container");
            const form = document.querySelector("#host_partener_main_form");
            var clone = form.cloneNode(true);
            clone.id = `host_partener_main_form_${this.form_count}`;
            clone.querySelector("select[name='country_id']").dataset.changeId = this.form_count
            clone.querySelector('.company_type_selection').remove()
            clone.reset();
            const country = clone.querySelector("select[name='country_id']");
            await ajax.jsonRpc("/get_states","call",{country_id:parseInt(country.value)})
           .then((res)=>{
                const country_state = clone.querySelector("select[name='state_id']");
                const options = country_state.options;
                const size = country_state.options.length;
                for(let i=size-1; i>=0; i--){
                    country_state.options.remove(options[i]);
                } 
                $.each(res, function(index, state){
                    const option = document.createElement('option');
                    option.text = state.name;
                    option.value = state.id;
                    country_state.appendChild(option);
                });
            })
            const h1 = document.createElement('h1');
            h1.textContent = `Host Site ${this.form_count}`;
            h1.classList.add('text-center');
            const targetDiv = clone.querySelector('.s_website_form_rows');
            targetDiv.parentNode.insertBefore(h1, targetDiv);
            container.appendChild(clone);
        },
        host_site_partner_remove(){
            if(this.form_count < 1) return;
            const form = document.getElementById( `host_partener_main_form_${this.form_count}`);
            form.remove();
            this.form_count--;
        },
        _submit: async function(ev){
            ev.preventDefault();
            var self = this;
            const $button = this.$target.find('#host_site_partner_submit, #host_site_partner_submit');
            $button.addClass('disabled') // !compatibility
                .attr('disabled', 'disabled');
            $('#host_site_partner_add').prop('disabled', true);
            $('#host_site_partner_remove').prop('disabled', true);
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);
            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }

        const main_form = document.getElementById('host_partener_main_form');
        if(main_form){
            const formData = new FormData(main_form);
            const formObjecData = {};
            formData.forEach((value,key)=>{
                formObjecData[key] = value;
            }) 
            await ajax.post($(main_form).attr('action')+ $(main_form).data('model_name'),formObjecData).then(async (res)=>{ 
                let data = JSON.parse(res);
                const taskID = data.id;
                if(taskID){
                    for(let i=1 ; i <= this.form_count; i++){
                        const form = document.getElementById(`host_partener_main_form_${i}`);
                        const formData = new FormData(form);
                        const formObjecData = {};
                        formData.forEach((value,key)=>{
                            formObjecData[key] = value;
                        })
                        formObjecData['partner_task_id'] = taskID.toString();
                        formObjecData['company_type'] = "Host Site";
                        await ajax.post($(form).attr('action')+ $(form).data('model_name'),formObjecData).then((res)=>{
                            if(i === this.form_count){
                                window.location.href = '/contactus-thank-you';
                            }
                        }).catch((err)=>{
                            console.error(err);  // Handle errors
                        });
                    }
                }else{
                      console.error("taskID is not set");
                }
            }).then(()=>{
                window.location.href = '/contactus-thank-you';
            }).catch((error) => {
                console.error("Error:", error);  // Handle errors
            });
        }
      
        },
        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    if (input.required && input.type === 'checkbox') {
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checkValidity());
                    } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'date')) {
                            return true;
                        }
                    } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'datetime')) {
                            return true;
                        }
                    }
                    return !input.checkValidity();
                });
                const $controls = $field.find('.form-control, .form-select, .form-check-input, .form-control-file');
                $field.removeClass('o_has_error');
                $controls.removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error');
                    $controls.addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({ content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top' });
                        const popover = Popover.getInstance($field);
                        popover._config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },
        update_status: function (status, message) {
            if (status !== 'success') {
                this.$target.find('#host_site_partner_submit, #host_site_partner_submit')
                    .removeAttr('disabled')
                    .removeClass('disabled'); // !compatibility
                this.restoreBtnLoading();
                this.displayNotification({
                    title: _t("Warning!"),
                    message: _t("Fill All Required Fields"), 
                    type:"danger", 
                })
                $('#host_site_partner_add').prop('disabled', false);
                $('#host_site_partner_remove').prop('disabled', false);
            }
            var $result = this.$('#s_website_form_result, #o_website_form_result'); // !compatibility

            if (status === 'error' && !message) {
                message = _t("An error has occured, the form has not been sent.");
            }
            this.__started.then(() => {
                $result.replaceWith(qweb.render(`website.s_website_form_status_${status}`, {
                    message: message,
                }))
            });
        },
    });
})


odoo.define('website.contact_form',function(require){
    'use strict';
    var core = require('web.core');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    const dom = require('web.dom');

    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.submitHrForm = publicWidget.Widget.extend({
        selector:'#wrap', 
        events:{
            'click .add_job': '_clone_form',  
            'click #remove_job': '_remove_form',
            'click .vaccancy_submit': 'send',
        },
        /**
         * @constructor
         */
        init: function(){
            this._super(...arguments);
            this.__started = new Promise(resolve => this.__startResolve = resolve);
            this.form_number = 1;
        },
        start(){
            this._super(...arguments);
            this.host_site();
        }, 
         async host_site(){
            const host = $("select[name='host_site_id']")
            if(host[0]){ 
                await ajax.jsonRpc("/get_host_type_partner","call",{"youth_company_type":"Host Site"})
                .then((res)=>{
                    host.empty();
                    $.each(res, function(index, state){
                        host.append($('<option>').text(state.name).attr('value', state.id));
                    });
                })
            }
        },
        _remove_form(ev){
            ev.preventDefault();
            if(this.form_number > 1){
                let form = document.getElementById(`vaccancy_${this.form_number}`);
                form.remove();
                const headers = document.querySelectorAll('.h1_class_job')
                let num = 1
                if(headers.length > 1){
                    for(let index=0; index < headers.length ; index++){
                        headers[index].classList.remove('d-none');
                        headers[index].textContent = `New Vacancy ${num}`;
                        num++;
                    }
                }else{
                    headers[0].classList.add('d-none');
                }
                this.form_number--;
            }  else {
                alert('Cannot remove the last job form');
            }

            if(this.form_number <= 1){
                $('#remove_job')[0].classList.add('d-none');
            }
        }, 
        _clone_form(ev){
            ev.preventDefault();
            $('#remove_job')[0].classList.remove('d-none');
            this.form_number++;
            const form = document.querySelector('.vaccancie_form');
            const form_container = document.getElementById('form_container');
            var clone = form.cloneNode(true);
            // clone.querySelector('.email_for_job').remove()
            clone.reset();
            clone.id = `vaccancy_${this.form_number}`;
            form_container.appendChild(clone);
            const headers = document.querySelectorAll('.h1_class_job')
            let num = 1
            for(let index=0; index < headers.length ; index++){
                headers[index].classList.remove('d-none');
                headers[index].textContent = `New Vacancy ${num}`;
                num++;
            }
        }, 
        _onchange_successPage(ev){
            if(ev.target.name === 'company_type'){
                const form = document.querySelector('#hr_recruitment_form');
                if(ev.target.value === 'Partner'){
                    form.dataset.successPage = '/create_partner';
                }else{
                    form.dataset.successPage = '/job-thank-you';
                }
            }
        },
        send: async function(e){
            $('#remove_job').prop('disabled', true);
            $('.add_job').prop('disabled', true);
            e.preventDefault();
            const $button = this.$target.find('.vaccancy_submit, .vaccancy_submit');
            $button.addClass('disabled') // !compatibility
                   .attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);
            var self = this;
            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
 
            this.form_fields = this.$('.vaccancie_form').serializeArray();
            $.each(this.$('.vaccancie_form').find('input[type=file]:not([disabled])'), (outer_index, input) => {
                $.each($(input).prop('files'), function (index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + outer_index + '][' + index + ']',
                        value: file
                    });
                });
            });

            var form_values = {};
            _.each(this.form_fields, function (input) {
                if (input.name in form_values) {
                    // If a value already exists for this field,
                    // we are facing a x2many field, so we store
                    // the values in an array.
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value !== '') {
                        form_values[input.name] = input.value;
                    }
                }
            });

             // force server date format usage for existing fields
             this.$('.vaccancie_form').find('.s_website_form_field:not(.s_website_form_custom)')
             .find('.s_website_form_date, .s_website_form_datetime').each(function () {
                 const inputEl = this.querySelector('input');
 
                 // Datetimepicker('viewDate') will return `new Date()` if the
                 // input is empty but we want to keep the empty value
                 if (!inputEl.value) {
                     return;
                 }
 
                 var date = $(this).datetimepicker('viewDate').clone().locale('en');
                 var format = 'YYYY-MM-DD';
                 if ($(this).hasClass('s_website_form_datetime')) {
                     date = date.utc();
                     format = 'YYYY-MM-DD HH:mm:ss';
                 }
                 form_values[inputEl.getAttribute('name')] = date.format(format);
             });

             const form_vals = [];
             const form_value_entries = Object.entries(form_values);
             if(this.form_number > 1){
                 for(let i =0; i < form_value_entries.length; i++){
                    let size = form_vals.length;
                    const key = form_value_entries[i][0];
                    for(let j = 0; j < form_value_entries[i][1].length; j++){
                        if(size === 0){
                            form_vals.push({
                                [key]: form_value_entries[i][1][j],
                            })
                        }else{
                            form_vals[j][key] = form_value_entries[i][1][j]
                        }
                    }
                 }
             }else{
                form_vals.push(form_values);
             }
 
             for(const dataDict of form_vals){
                let job_vaccancy = parseInt(dataDict['vacancies']);
                dataDict['email_from'] = 'yhh@warlocktechnologies.com';
                for(let i= job_vaccancy ; i >0 ; i--){
                    await ajax.post(this.$('.vaccancie_form').attr('action') + this.$('.vaccancie_form').data('model_name'),dataDict);
                } 
             }

             window.location.href = '/contactus-thank-you';

        }, 
        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    if (input.required && input.type === 'checkbox') {
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checkValidity());
                    } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'date')) {
                            return true;
                        }
                    } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'datetime')) {
                            return true;
                        }
                    }
                    return !input.checkValidity();
                });
                const $controls = $field.find('.form-control, .form-select, .form-check-input, .form-control-file');
                $field.removeClass('o_has_error');
                $controls.removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error');
                    $controls.addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                        const popover = Popover.getInstance($field);
                        popover._config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },
        update_status: function (status, message) {
            if (status !== 'success') { 
                this.$target.find('.vaccancy_submit, .vaccancy_submit')
                    .removeAttr('disabled')
                    .removeClass('disabled'); // !compatibility
                this.restoreBtnLoading();
                $('#remove_job').prop('disabled', false);
                $('.add_job').prop('disabled', false);
            }
            var $result = this.$('#s_website_form_result, #o_website_form_result'); // !compatibility

            if (status === 'error' && !message) {
                message = _t("An error has occured, the form has not been sent.");
            }
            this.__started.then(() => { 
                $result.replaceWith(qweb.render(`website.s_website_form_status_${status}`, {
                message: message,
            }))});
        },
    })

}) 
odoo.define('website.employee_weekly_task', function (require) {
'use strict';

var Dialog = require('web.Dialog');
var publicWidget = require('web.public.widget');

publicWidget.registry.employee_weekly_task = publicWidget.Widget.extend({
    selector: '#wt_employee_timesheet',
    events: {
        'change #superwiser': '_onChangeSuperwiser',
        'change #employee': '_onChangeEmployee',
        'click #show_employee_timesheet': '_on_show_employee_timesheet',
    },
    
    start: function () {
        // Dialog.alert(this, "Hello, world!");
        return this._super.apply(this, arguments);
    },
    
    _onChangeSuperwiser: async function (ev) {
        var selection_html = '<option value="" selected="true">Select</option>'
        if(ev.target.value){
            const superwiser_id = parseInt(ev.target.value, 10);
            var employees = await this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['parent_id', '=', superwiser_id]], ['id','name']],
            });
            
            for (const employee of employees) {
               selection_html += '<option value="'+employee.id+'">'+employee.name+'</option>'
            }
        }
        $('select[id="employee"]').html(selection_html)
    },
    
    _onChangeEmployee: async function (ev) {
        var selection_html = '<option value="" selected="true">Select</option>'
        if(ev.target.value){
            const employee_id = parseInt(ev.target.value, 10);
            var tasks = await this._rpc({
                model: 'project.task',
                method: 'search_read',
                args: [[['employee_id', '=', employee_id],['project_id','=',7]], ['id','name']],
            });
            
            for (const task of tasks) {
               selection_html += '<option value="'+task.id+'">'+task.name+'</option>'
            }
        }
        $('select[id="task_id"]').html(selection_html)
    },
    
    _on_show_employee_timesheet: async function (ev) {
        $('select[id="superwiser"]').removeClass('is-invalid')
        $('select[id="employee"]').removeClass('is-invalid')
        $('select[id="task_id"]').removeClass('is-invalid')
        
        $('#task_week_date').html('<div class="col-md-6">Week Start: </div><div class="col-md-6">Week End: </div>')
        $('#wt_employee_task_table_body').html('')
        
        if(!$('select[id="superwiser"]').val()){
            $('select[id="superwiser"]').addClass('is-invalid')
        }else if(!$('select[id="employee"]').val()){
            $('select[id="employee"]').addClass('is-invalid')
        }else if(!$('select[id="task_id"]').val()){
            $('select[id="task_id"]').addClass('is-invalid')
        }else{
            var task_id = parseInt($('select[id="task_id"]').val(), 10)
            var task = await this._rpc({
                model: 'project.task',
                method: 'search_read',
                args: [[['id', '=', task_id]], ['id','name', 'week_start','week_end', 'weekly_tasks_ids']],
            });
            var task_date_html = '<div class="col-md-6">Week Start: '+ (task[0].week_start || "") +'</div><div class="col-md-6">Week End: '+ (task[0].week_end || "") +'</div>'
            $('#task_week_date').html(task_date_html)
         
            if(task[0].weekly_tasks_ids){
                var weekly_tasks_ids = await this._rpc({
                    model: 'project.task',
                    method: 'search_read',
                    args: [[['id', 'in', task[0].weekly_tasks_ids]], ['id','name', 'daily_start_time','daily_end_time','daily_duties', 'daily_attendance_status']],
                });
                var weekly_task_html = ''
                var weekly_task_count = 0
                for (const weekly_task of weekly_tasks_ids) {
                    weekly_task_count += 1
                    weekly_task_html += '<tr> <td>'+ weekly_task_count +'</td> <td>'+ (weekly_task.name || "" ) +'</td> <td>'+ (weekly_task.daily_start_time || "" ) +'</td> <td>'+ (weekly_task.daily_end_time || "" ) +'</td> <td>'+ (weekly_task.daily_duties || "" ) +'</td><td>'+ (weekly_task.daily_attendance_status || "" ) +'</td> </tr>'
                }
                $('#wt_employee_task_table_body').html(weekly_task_html)
                
            }
            
        }
        
    }
})
});

odoo.define('create_partner_editor.weekly_register', function (require) {
    'use strict';
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    const dom = require('web.dom');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.WeeklyRegister = publicWidget.Widget.extend({
        selector: '#wrap',
        events: {
            'click #add_timesheet': '_add_timesheet',
            'click #remove_timesheet': '_remove_line',
            'change .daily_status': '_change_daily_status',
            'click .weekly_submit_btn': '_submit_btn',
            'blur .datetimepicker-input': '_date_validation',
        },
        init() {
            this._super(...arguments);
            this.__started = new Promise(resolve => this.__startResolve = resolve);
        },
        start() {
            this._super(...arguments);
            this.timesheet_number = 1;
        },
        _submit_btn: async function (ev) {
            ev.preventDefault();
            var self = this;
            const $button = this.$target.find('.weekly_submit_btn, .weekly_submit_btn');
            $button.addClass('disabled') // !compatibility
                .attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);
            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
            this.form_fields = this.$('form').serializeArray();
            $.each(this.$('form').find('input[type=file]:not([disabled])'), (outer_index, input) => {
                $.each($(input).prop('files'), function (index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + outer_index + '][' + index + ']',
                        value: file
                    });
                });
            });

            var form_values = {};
            _.each(this.form_fields, function (input) {
                if (input.name in form_values) {
                    // If a value already exists for this field,
                    // we are facing a x2many field, so we store
                    // the values in an array.
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value !== '') {
                        form_values[input.name] = input.value;
                    }
                }
            });

            this.$('form').find('.s_website_form_field:not(.s_website_form_custom)')
                .find('.s_website_form_date, .s_website_form_datetime').each(function () {
                    const inputEl = this.querySelector('input');

                    // Datetimepicker('viewDate') will return `new Date()` if the
                    // input is empty but we want to keep the empty value
                    if (!inputEl.value) {
                        return;
                    }

                    var date = $(this).datetimepicker('viewDate').clone().locale('en');
                    var format = 'YYYY-MM-DD';
                    if ($(this).hasClass('s_website_form_datetime')) {
                        date = date.utc();
                        format = 'YYYY-MM-DD HH:mm:ss';
                    }
                    form_values[inputEl.getAttribute('name')] = date.format(format);
                });

            this.task_ids = []; 
            
            // Here we will create a task for timesheets
            for (let i = 0;  i < this.timesheet_number; i++) {
                this.child_form_vals = {};
                let numb = i+1;
                const task_div = document.querySelector(`.register_timesheet_container_${numb}`); 
                const task_selection = task_div.querySelector('.daily_status'); 
                const file_input = task_div.querySelector("input[name='register_doc']"); 

                // Differntite the value for Single Task
                if(this.timesheet_number === 1){
                    this.child_form_vals['email_from'] = form_values['email_from'];
                    this.child_form_vals['daily_end_time'] = form_values['daily_end_time_1'];
                    this.child_form_vals['name'] = form_values['name'];
                    this.child_form_vals['daily_start_time'] = form_values['daily_start_time_1'];
                    this.child_form_vals['project_id'] = form_values['project_id'];
                    if(task_selection.value){
                        this.child_form_vals['daily_attendance_status'] = form_values['daily_status'];
                        if(task_selection.value !== 'Present' && file_input){
                            if(file_input.value){
                                this.child_form_vals['register_doc'] = form_values['register_doc[0][0]'];
                            }
                        }
                    }
                }else{
                    this.child_form_vals['email_from'] = form_values['email_from'];
                    this.child_form_vals['project_id'] = form_values['project_id'];
                    this.child_form_vals['name'] = form_values['name'][i];
                    this.child_form_vals['daily_start_time'] = form_values[`daily_start_time_${numb}`];
                    this.child_form_vals['daily_end_time'] = form_values[`daily_end_time_${numb}`];
                    this.child_form_vals['daily_attendance_status'] = form_values['daily_status'][i];

                    if(form_values['daily_status'][i] !== 'Present' && file_input){
                        if(file_input.value){
                            this.child_form_vals['register_doc'] = form_values[`register_doc[${i}][0]`];
                        }
                    }

                }
                await ajax.post(this.$('form').attr('action') + this.$('form').data('model_name'), this.child_form_vals).then((res)=>{
                    let parsed_dict = JSON.parse(res);
                    this.task_ids.push(parsed_dict.id);
                })
            }

            // Here is the main Task Created will append it id
            let values = {
                'name': form_values['task_name'],
                'project_id': form_values['project_id'],
                'email_from': form_values['email_from'],
                'week_start': form_values['week_start'],
                'week_end': form_values['week_end'],
                'employee_id': form_values['employee_id'],
                'weekly_tasks_ids': this.task_ids,
            };
            this.task_id = false;
            await ajax.post(this.$('form').attr('action') + this.$('form').data('model_name'), values).then(async (res) => {
                let parsed_dict = JSON.parse(res);
                this.task_id = parsed_dict.id;
            });
            window.location.href = '/contactus-thank-you';
            // Let's create the main task

        },
        _add_timesheet(ev) {
            ev.preventDefault();
            $('#remove_timesheet')[0].classList.remove('d-none');
            const timesheet = document.querySelector(`.register_timesheet_container_${this.timesheet_number}`);
            let new_entry = timesheet.cloneNode(true);
            let temp = this.timesheet_number + 1; //For Update the value we will use temp otherwise I need previus value for gettting in querySelector
            new_entry.className = `register_timesheet_container_${temp}`;
            new_entry.querySelector('h3').textContent = `Day ${temp}`

            // Now It will Take a long code but I need to adjust the different id otherwise bootstrap datePicker will not work

            // For Start Time 
            const start_time_label = new_entry.querySelector('.website_start_time_label');
            $(start_time_label).prop('for', `daily_start_time_${temp}`);
            const start_time_div = new_entry.querySelector(`#datetimepicker_daily_start_time_${this.timesheet_number}`);
            start_time_div.id = `datetimepicker_daily_start_time_${temp}`;
            const start_time_input = start_time_div.querySelector('input');
            const start_time_div_child = start_time_div.querySelector('div');
            start_time_input.id = `daily_start_time_${temp}`;
            start_time_input.name = `daily_start_time_${temp}`;
            start_time_input.dataset.target = `#datetimepicker_daily_start_time_${temp}`;
            start_time_input.dataset.id = temp;
            start_time_div_child.dataset.target = `#datetimepicker_daily_start_time_${temp}`;
            start_time_input.value = '';

            // For End Time 
            const end_time_label = new_entry.querySelector('.website_end_time_label');
            $(end_time_label).prop('for', `daily_end_time_${temp}`);
            const end_time_div = new_entry.querySelector(`#datetimepicker_daily_end_time_${this.timesheet_number}`);
            end_time_div.id = `datetimepicker_daily_end_time_${temp}`;
            const end_time_input = end_time_div.querySelector('input');
            const end_time_div_child = end_time_div.querySelector('div');
            end_time_input.id = `daily_end_time_${temp}`;
            end_time_input.name = `daily_end_time_${temp}`;
            end_time_input.dataset.id= temp
            end_time_input.value = '';
            end_time_input.dataset.target = `#datetimepicker_daily_end_time_${temp}`;
            end_time_div_child.dataset.target = `#datetimepicker_daily_end_time_${temp}`;


            // For Selection Field 
            const selection_input = new_entry.querySelector('.daily_status');
            selection_input.id = `daily_status_${temp}`;
            selection_input.dataset.id = temp;
            selection_input.value = '';

            // For Register Attachment Input 
            const register_div = new_entry.querySelector(`#daily_register_${this.timesheet_number}`);
            register_div.id = `daily_register_${temp}`;
            register_div.classList.remove('d-none');
            new_entry.querySelector("input[name='register_doc']").value = ''

            // For Title value 
            const title_input = new_entry.querySelector(`.daily_title_${this.timesheet_number}`);
            title_input.classList.remove(`daily_title_${this.timesheet_number}`);
            title_input.classList.add(`daily_title_${temp}`);
            title_input.value = '';

            timesheet.after(new_entry);
            this.timesheet_number++;
            if (this.timesheet_number === 7) {
                $('#add_timesheet')[0].classList.add('d-none');
            }
        },
        _remove_line(ev) {
            ev.preventDefault();
            if (this.timesheet_number === 1) return;
            $('#add_timesheet')[0].classList.remove('d-none');
            const div_container = document.querySelector(`.register_timesheet_container_${this.timesheet_number}`);
            div_container.remove();
            this.timesheet_number--;  // Decrement the counter as we are removing a line.
            if (this.timesheet_number === 1) $('#remove_timesheet')[0].classList.add('d-none');
        },
        _change_daily_status(ev) {
            let datasetId = ev.target.dataset.id;
            if (ev.target.value === 'Present') {
                $(`#daily_register_${datasetId}`)[0].classList.add('d-none')
            } else {
                $(`#daily_register_${datasetId}`)[0].classList.remove('d-none')
            }
        },
        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            // Loop on all fields
            this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');

                // Validate inputs for this field
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    if (input.required && input.type === 'checkbox') {
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checkValidity());
                    } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'date')) {
                            return true;
                        }
                    } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'datetime')) {
                            return true;
                        }
                    }
                    return !input.checkValidity();
                });
                const $controls = $field.find('.form-control, .form-select, .form-check-input, .form-control-file');
                $field.removeClass('o_has_error');
                $controls.removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error');
                    $controls.addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({ content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top' });
                        const popover = Popover.getInstance($field);
                        popover._config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            return form_valid;
        },
        update_status: function (status, message) {
            if (status !== 'success') {
                this.$target.find('.vaccancy_submit, .vaccancy_submit')
                    .removeAttr('disabled')
                    .removeClass('disabled'); // !compatibility
                this.restoreBtnLoading();
                $('#remove_job').prop('disabled', false);
                $('.add_job').prop('disabled', false);
            }
            var $result = this.$('#s_website_form_result, #o_website_form_result'); // !compatibility

            if (status === 'error' && !message) {
                message = _t("An error has occured, the form has not been sent.");
            }
            this.__started.then(() => {
                $result.replaceWith(qweb.render(`website.s_website_form_status_${status}`, {
                    message: message,
                }))
            });
        },
       _date_validation(ev){
            if(ev.target.name === 'week_end' || ev.target.name === 'week_start'){
                let week_start_input = $("input[name='week_start']");
                let week_end_input = $("input[name='week_end']");               
                if(week_end_input.val() && week_start_input.val()){
                    let week_start = new Date(week_start_input.val()); 
                    let week_end = new Date(week_end_input.val()); 
                    const millisecondDiff = week_end.getTime() - week_start.getTime();
                    const daysDiff  = millisecondDiff / (1000 *60*60*24);
                    if(daysDiff < 6 || daysDiff > 6){
                        week_end_input.val('');
                        alert("Week End Date must be select after 7 Days");
                    }
                }
                return
            } 
            // Here we will check the start time and end time using datasetId
            let datasetId = ev.target.dataset.id;

            let start_time = $(`input[name='daily_start_time_${datasetId}']`);
            let end_time = $(`input[name='daily_end_time_${datasetId}']`);

            if(start_time.val() && end_time.val()){
                let start_time_value = new Date(start_time.val());
                let end_time_value = new Date(end_time.val());
                if(start_time_value.getDate() != end_time_value.getDate()){
                    alert("Start time and end time should be on the same day.");
                    end_time.val(''); 
                    return
                }

                const time_diff = end_time_value.getTime() - start_time_value.getTime();
                if(time_diff < 0){
                    alert("Start Should be smaller that End Time!");
                    end_time.val('');
                }
            }
        }
    })
}) 