# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError
from odoo.exceptions import ValidationError

class DepartmentInherit(models.Model):
    _inherit = "hr.department"
       
    pheduyet_dgthuviec_id = fields.Many2one('hr.employee', "Phê duyệt ĐG thử việc", tracking=True)
    