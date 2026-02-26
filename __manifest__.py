{
    'name': 'Employee Operations',
    'author': 'Mahmoud Eltawel',
    'category': '',
    'version': '19.0.1.0',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/employee_task_view.xml',
        'views/sale_request_view.xml',
        'views/hr_employee_view.xml',
        'views/base_menu.xml',
        'reports/employee_report.xml'],
    'application': True
}