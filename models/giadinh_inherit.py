# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class Resume_line_inherit(models.Model):
    _inherit = "hr.ttgiadinh"    
        
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    
    