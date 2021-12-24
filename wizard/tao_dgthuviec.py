# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class TaoDGThuviec(models.TransientModel):
    _name = "hr.tao.dgthuviec"
    _description = "Tạo đánh giá thử việc"    

    nhansu_tu_danhgia = fields.Selection([
        ('tudanhgia', 'Tự đánh giá'),
        ('quanlydanhgia', 'Quản lý trực tiếp đánh giá'),      
        ('boqua', 'Bỏ qua bước tự đánh giá'),        
    ], string="Nhân sự tự đánh giá", required=True)   

    def hoanthanh(self):
        for rec in self:
            employee = self.env['hr.employee'].browse(self.env.context.get('active_ids')) 
            employee.tao_dgthuviec(rec.nhansu_tu_danhgia)
            return True