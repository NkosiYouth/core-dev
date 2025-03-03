# -*- coding: utf-8 -*-
{
    'name':'Youth Work Host Site and Partners',
    'version':'17.0.0.1',
    'summary':'Youth Work Host Site and Partners',
    'description':'Youth Work Host Site and Partners',
    'author': 'Warlock Technologies Pvt Ltd.',
    'category':'Category',
    'website': 'https://www.warlocktechnologies.com',
    'depends':["web","base",'project',"website","hr","helpdesk_mgmt_project","hr_timesheet","survey","sale_project",'timer','sale','account',"mass_mailing",'sms'],
    'data':[
       "security/ir.model.access.csv",
        "views/project_task.xml",
        "views/host_site_partner.xml",
        "data/data.xml",
        'data/calender_mail_template.xml',
        "views/youth_application.xml",
        "views/hr_issue.xml",
        "views/job_vacancies.xml",
        "views/res_partner_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/hr_employee_views.xml",
        "views/journey_journey_view.xml",
        "views/hr_expense_views.xml",
        "views/user_role_view.xml",
        "views/cohort_view.xml",
        "views/survey_survey_view.xml",
        "views/hr_contract_view.xml",
        "views/project_project_view.xml",
        "views/resignation.xml",
        "views/survey_templates.xml",
        "views/survey_question_view.xml",
        "views/res_bank_view.xml",
        "views/res_partner_bank_view.xml",
        "views/helpdesk_ticket_team_views.xml",
        "views/hr_leave_type_view.xml",
        "views/hr_leave_view.xml",
        "views/portal_view.xml",
        "views/mailing_mailing_view.xml",
        "views/res_config_settings_view.xml",
        "views/sms_composer_view.xml",
        "views/leave_portal_form_view.xml",
        "views/importer_youth_view.xml",
        "views/res_contact_views.xml",
        "views/hr_employee_views_list.xml",
        "wizard/weekly_register_update_stage.xml",
        'views/office_view.xml'
    ],
    'assets':{
         "web.assets_frontend":[
            "/wt_customization/static/src/js/script.js",
            "/wt_customization/static/src/js/leave_form.js"
        ],
        'web.assets_backend': [
            # "/wt_customization/static/src/js/countdown.js"
        ],
        "survey.survey_assets": [
        "/wt_customization/static/src/js/survey_form.js"
        ]
    },
    'external_dependencies': {},
    # 'images':['static/images/screen_image.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    "price": 00,
    "currency": "USD",
}