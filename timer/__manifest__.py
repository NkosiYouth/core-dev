{
    'name':'Record Time',
    'version':'17.0.0.1',
    'summary':'Record time',
    'description':'Record time',
    'author': 'Warlock Technologies Pvt Ltd.',
    'category':'Services/Timesheets',
    'website': 'https://www.warlocktechnologies.com',
    'depends': ['web', 'mail'],
    'data': [
        'security/timer_security.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'timer/static/src/**/*',
        ],
        'web.qunit_suite_tests': [
            'timer/static/tests/**/*',
        ],
    }
}