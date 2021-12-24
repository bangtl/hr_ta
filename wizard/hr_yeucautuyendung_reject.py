# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class YeucautuyendungReject(models.TransientModel):
    _name = "hr.yeucautuyendung.tuchoi"
    _description = "Từ chối yêu cầu tuyển dụng"

    lydo =  fields.Char("Lý do")   

    def xacnhan(self):
        yeucautuyendung = self.env['hr.yeucautuyendung'].browse(self.env.context.get('active_ids'))
        yeucautuyendung.send_email_tuchoi(self.lydo,yeucautuyendung.user_id)
        yeucautuyendung.reject()
        return True