# -*- coding:utf-8 -*-

{
    'name': 'HRM TA Module',
    'category': 'Human Resources/Employees',
    'version': '14.0',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'hr_od',
        'hr_skills',
    ],
    'data': [        
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/hr_yeucautuyendung.xml',        
        'views/hr_applicant_inherit.xml',
        'views/hr_skill_inherit.xml',
        'views/hr_job_inherit.xml',
        'views/hr_dgungvien.xml',
        'views/hr_dgthuviec.xml',  
        'views/hr_employee_inherit.xml',
        'views/hr_department_inherit.xml',
        'report/thumoinhanviec_report.xml',
        'data/mail_template.xml',
        'data/automation.xml',
        'wizard/hr_dgthuviec_reject.xml',
        'wizard/hr_yeucautuyendung_reject.xml',
        'wizard/assign_to.xml',
        'wizard/tao_dgungvien.xml',
        'wizard/tao_dgthuviec.xml',
    ],
    # 'demo': [
    # ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
