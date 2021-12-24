# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class AssignTo(models.TransientModel):
    _name = "hr.yeucautuyendung.assign.to"
    _description = "Chuyển tiếp yêu cầu"

    user_id = fields.Many2one('res.users', string='Người xử lý')   

    def xacnhan(self):
        yctuyendung = self.env['hr.yeucautuyendung'].browse(self.env.context.get('active_ids'))        
        yctuyendung.update({'user_id': self.user_id.id})        
        return True