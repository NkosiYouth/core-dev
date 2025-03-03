odoo.define('survey.tour_test_certification_success', function (require) {
    'use strict';

    var SurveyFormWidget = require('survey.form');

    SurveyFormWidget.include({
        _prepareSubmitValues: function (formData, params) {
            var self = this;
            formData.forEach(function (value, key) {
                switch (key) {
                    case 'csrf_token':
                    case 'token':
                    case 'page_id':
                    case 'question_id':
                        params[key] = value;
                        break;
                }
            });

            // Get all question answers by question type
            this.$('[data-question-type]').each(function () {
                switch ($(this).data('questionType')) {
                    case 'text_box':
                    case 'user_id':
                    case 'char_box':
                    case 'numerical_box':
                        params[this.name] = this.value;
                        break;
                    case 'date':
                        params = self._prepareSubmitDates(params, this.name, this.value, false);
                        break;
                    case 'datetime':
                        params = self._prepareSubmitDates(params, this.name, this.value, true);
                        break;
                    case 'simple_choice_radio':
                    case 'multiple_choice':
                        params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                        break;
                    case 'matrix':
                        params = self._prepareSubmitAnswersMatrix(params, $(this));
                        break;
                    case 'upload_file': // Added file upload support
                        params[this.name] = [
                            JSON.parse($(this).attr('data-oe-data') || "[]"),
                            JSON.parse($(this).attr('data-oe-file_name') || "[]")
                        ];
                        break;
                }
            });
        },

        events: _.extend({}, SurveyFormWidget.prototype.events, {
            'change .o_survey_upload_file': '_onFileChange',
        }),

        _onFileChange: function (event) {
            var self = this;
            var files = event.target.files;
            var fileNames = [];
            var dataURLs = [];

            if (!files.length) return;

            var processFile = function (file, index) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var dataURL = e.target.result.split(',')[1]; // Extract base64
                    fileNames[index] = file.name;
                    dataURLs[index] = dataURL;

                    if (fileNames.length === files.length) {
                        self._updateFileInputs(fileNames, dataURLs);
                    }
                };
                reader.readAsDataURL(file);
            };

            for (let i = 0; i < files.length; i++) {
                processFile(files[i], i);
            }
        },

        _updateFileInputs: function (fileNames, dataURLs) {
            var $input = this.$el.find('input.o_survey_upload_file');
            $input.attr('data-oe-data', JSON.stringify(dataURLs));
            $input.attr('data-oe-file_name', JSON.stringify(fileNames));

            // Update File List UI
            var fileList = document.getElementById('fileList');
            fileList.innerHTML = '';

            var ul = document.createElement('ul');
            fileNames.forEach(function (fileName) {
                var li = document.createElement('li');
                li.textContent = fileName;
                ul.appendChild(li);
            });

            var deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete All';
            deleteBtn.addEventListener('click', function () {
                fileList.innerHTML = '';
                $input.attr('data-oe-data', '');
                $input.attr('data-oe-file_name', '');
                $input.val('');
            });

            fileList.appendChild(ul);
            fileList.appendChild(deleteBtn);
        },
    });
});
