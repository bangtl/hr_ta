# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class HRDGThuviecReject(models.TransientModel):
    _name = "hr.dgthuviec.tuchoi"
    _description = "Từ chối đánh giá thử việc"

    lydo =  fields.Char("Lý do")   

    def xacnhan(self):
        dgthuviec = self.env['hr.dgthuviec'].browse(self.env.context.get('active_ids'))
        #dgthuviec.update({'trangthai_id': self.env.ref('hr_thcorp_ta.dgthuviec_stage_3').id}) 
        dgthuviec.update({'tpdg_xong': False})
        dgthuviec.update({'user_id': dgthuviec.manager_id.id}) 
        dgthuviec.send_email_tuchoi(self.lydo) 
        return True