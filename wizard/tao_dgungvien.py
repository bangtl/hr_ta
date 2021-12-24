# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

class TaoDGUngvien(models.TransientModel):
    _name = "hr.tao.dgungvien"
    _description = "Tạo đánh giá ứng viên"

    tinhcach_ids = fields.Many2many('hr.applicant.tinhcach', string='Tính cách')
    chiuapluc = fields.Selection([
        ('cao', 'Cao'),
        ('trungbinh', 'Trung bình'),
        ('thap', 'Thấp')
    ], string="Khả năng chịu áp lực")
    dienmao_tacphong =  fields.Char("Diện mạo/ Tác phong")    
    giongnoi =  fields.Char("Giọng nói") 
    phuhop_vanhoa =  fields.Char("Mức độ phù hợp VH Cty")
    kt_chuyenmon =  fields.Char("Kiến thức chuyên môn")
    kn_giaotiep =  fields.Char("Kỹ năng giao tiếp")
    trinhbay_diendat =  fields.Char("Trình bày/ Diễn đạt")
    td_ngoaingu =  fields.Char("Trình độ Ngoại ngữ")
    td_vitinh =  fields.Char("Trình độ Vi tính")
    kn_khac =  fields.Char("Kỹ năng khác")
    nsdg_phuhop = fields.Text("Điểm phù hợp (NS)")
    nsdg_hanche = fields.Text("Điểm hạn chế (NS)")

    loai_tgthuviec = fields.Selection([
        ('ngay', 'Ngày'),
        ('thang', 'Tháng')   
    ], string="Thử việc theo", default='ngay')

    tg_thuviec = fields.Integer(string='TG thử việc', default=60)

    tgthuviec_id = fields.Many2one('hr.tgthuviec', string='Thời gian thử việc', required=True)

    thuviec_tu = fields.Date('Thử việc từ ngày')
    thuviec_den = fields.Date('Thử việc đến ngày', compute='_compute_thuviecden', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Loại tiền', default=lambda self: self._get_default_currency_id(), required=True)
    
    luong_chinh = fields.Monetary(string='Lương chính')  
    pt_thuviec = fields.Float(string='Tỷ lệ Lương thử việc', default=85, compute='_compute_tylethuviec', store=True, readonly=False)  
    luong_thuviec = fields.Monetary(string='Lương thử việc', compute='_compute_luongthuviec', store=True, readonly=False) 
    
    def _get_default_currency_id(self):
        applicant = self.env['hr.applicant'].browse(self.env.context.get('active_ids')) 
        return applicant.currency_id

    @api.depends('tgthuviec_id','thuviec_tu')
    def _compute_thuviecden(self):
        for rec in self:
            if rec.tgthuviec_id and rec.thuviec_tu:  
                thogian = rec.tgthuviec_id.thoigian
                rec.thuviec_den = rec.thuviec_tu + timedelta(days=thogian-1)                
            else:
                rec.thuviec_den = False

    @api.depends('luong_chinh', 'pt_thuviec')
    def _compute_luongthuviec(self):
        for rec in self:
            rec.luong_thuviec = rec.luong_chinh * (rec.pt_thuviec/100)

    @api.depends('luong_chinh', 'luong_thuviec')
    def _compute_tylethuviec(self):
        for rec in self:
            if rec['luong_chinh'] > 0:
                rec['pt_thuviec'] = (rec.luong_thuviec * 100)/rec.luong_chinh 

    def hoanthanh(self):
        for rec in self:
            applicant = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))       
            dgungvien_search = self.env["hr.dgungvien"].sudo().search([("applicant_id", "=", applicant.id),("active", "=", True)])
            if not dgungvien_search:
                self.env['hr.dgungvien'].sudo().create({                    
                    'applicant_id': applicant.id,
                    'user_id': applicant.nguoi_pv_id.id,
                    'nsdg_xong': True,                    
                    'stage_id': self.env.ref('hr_ta.dgungvien_stage_2').id,
                    'tinhcach_ids': rec.tinhcach_ids,
                    'chiuapluc': rec.chiuapluc,
                    'dienmao_tacphong': rec.dienmao_tacphong,
                    'giongnoi': rec.giongnoi,
                    'phuhop_vanhoa': rec.phuhop_vanhoa,
                    'kt_chuyenmon': rec.kt_chuyenmon,
                    'kn_giaotiep': rec.kn_giaotiep,
                    'trinhbay_diendat': rec.trinhbay_diendat,
                    'td_ngoaingu': rec.td_ngoaingu,
                    'td_vitinh': rec.td_vitinh,
                    'kn_khac': rec.kn_khac,
                    'nsdg_phuhop': rec.nsdg_phuhop,
                    'nsdg_hanche': rec.nsdg_hanche,
                    'tgthuviec_id': rec.tgthuviec_id.id,                    
                    'thuviec_tu': rec.thuviec_tu,
                    'thuviec_den': rec.thuviec_den,
                    'luong_chinh': rec.luong_chinh,
                    'pt_thuviec': rec.pt_thuviec,
                    'luong_thuviec': rec.luong_thuviec,
                })            
                applicant.update({'dataodanhgia': True})    
                message_id = self.env['message.wizard'].create({'message':("Tạo đánh giá ứng viên thành công.")})
                return {
                    'name': ('Successfull'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'message.wizard',
                    # pass the id
                    'res_id': message_id.id,
                    'target': 'new'
                }
            else:
                raise UserError("Đã tạo Đánh giá Ứng viên!")           
            return True