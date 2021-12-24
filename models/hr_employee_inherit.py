# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from openerp.exceptions import UserError
import math

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Char('Message')
    
    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}

class EmployeeInherit(models.Model):
    _inherit = "hr.employee"
    
    nguoituyendung_id = fields.Many2one('res.users', string='Người tuyển dụng')
    khthuviec_count =  fields.Integer("Kế hoạch thử việc", compute='_compute_khthuvieccount')
    dgthuviec_count =  fields.Integer("Đánh giá thử việc", compute='_compute_dgthuvieccount')
    dgungvien_count =  fields.Integer("Đánh giá ứng viên", compute='_compute_dgungviencount')
    applicant_count =  fields.Integer("Sô lượng Ứng viên", compute='_compute_applicantcount')

    def get_user_id(self,employee):
        user = False
        if employee:
            user_id = self.env["res.users"].sudo().search([('employee_id','=',employee.id)]) 
            if user_id:
                user = user_id                     
        return user

    @api.depends('write_date')
    def _compute_khthuvieccount(self):
        for rec in self:
            khthuviec_count = self.env["hr.khthuviec"].sudo().search_count([("employee_id", "=", rec.id)])
            rec['khthuviec_count'] = khthuviec_count
    
    @api.depends('write_date')
    def _compute_dgthuvieccount(self):
        for rec in self:
            dgthuviec_count = self.env["hr.dgthuviec"].sudo().search_count([("employee_id", "=", rec.id)])
            rec['dgthuviec_count'] = dgthuviec_count

    @api.depends('write_date')
    def _compute_applicantcount(self):
        for rec in self:
            applicant_count = self.env["hr.applicant"].sudo().search_count([("emp_id", "=", rec.id)])
            rec['applicant_count'] = applicant_count

    @api.depends('write_date')
    def _compute_dgungviencount(self):
        for rec in self:
            dgungvien_count = self.env["hr.dgungvien"].sudo().search_count([("employee_id", "=", rec.id)])
            rec['dgungvien_count'] = dgungvien_count

   
    # Tạo kế hoạch thử việc
    def tao_khthuviec(self):       
        for rec in self:  
            khthuviec_search = self.env["hr.khthuviec"].sudo().search([("employee_id", "=", rec.id),("active", "=", True)])
            if not khthuviec_search:
                contract = self.env["hr.contract"].sudo().search([("employee_id", "=", rec.id), ('loaihd_id', '=', self.env.ref('hr_employee_contract.hr_contract_type_1').id)])
                if contract:
                    for c in contract:                    
                        batdau_thuviec = c.date_start                        
                        ketthuc_thuviec = c.date_end    
                else:
                    raise UserError("Chưa tạo Hợp đồng!")

                # Lấy user của người quản lý trực tiếp
                if rec.parent_id and rec.parent_id.nguoikiemnhiem_id:
                    parent_user = rec.get_user_id(rec.parent_id.nguoikiemnhiem_id)
                elif rec.parent_id:
                    parent_user = rec.get_user_id(rec.parent_id)
                else:
                    parent_user = False
                
                if rec.user_id and parent_user != False and contract:
                    new_kh_thuviec = self.env['hr.khthuviec'].sudo().create({        
                        'employee_id': rec.id,
                        'user_id': parent_user.id,                   
                        'batdau_thuviec': batdau_thuviec,
                        'ketthuc_thuviec': ketthuc_thuviec,                
                    })
                    message_id = self.env['message.wizard'].create({'message':("Tạo kế hoạch thử việc thành công.")})
                    return {
                        'name': ('Successfull'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'message.wizard',
                        # pass the id
                        'res_id': message_id.id,
                        'target': 'new'
                    }
                elif not rec.user_id:
                    raise UserError("Nhân viên chưa có user!")
                elif parent_user == False:
                    raise UserError("Nhân viên chưa có Quản lý trực tiếp!")                
                elif not contract:
                    raise UserError("Chưa tạo hợp đồng!")  
            else:
                raise UserError("Đã tạo Kế hoạch thử việc!")  
    
    def tao_dgthuviec(self,nhansu_tu_danhgia):       
        for rec in self:
            dgthuviec_search = self.env["hr.dgthuviec"].sudo().search([("employee_id", "=", rec.id),("active", "=", True)])
            if not dgthuviec_search:
                # Tìm và kiểm tra hợp đồng
                contract = self.env["hr.contract"].sudo().search([("employee_id", "=", rec.id), ('loaihd_id', '=', self.env.ref('hr_employee_contract.hr_contract_type_1').id)])
                if contract:
                    for c in contract:                               
                        ngaykt_thuviec = c.date_end    
                        luong_thuviec = c.wage       
                        ngay_kyhd = c.date_end + timedelta(days=1)
                else:
                    raise UserError("Chưa tạo Hợp đồng!")
                # Nếu là nhân sự tự đánh giá
                if nhansu_tu_danhgia == 'tudanhgia':
                    if rec.user_id:
                        new_dg_thuviec = self.env['hr.dgthuviec'].sudo().create({        
                            'employee_id': rec.id,
                            'user_id': rec.user_id.id,
                            'ngaykt_thuviec': ngaykt_thuviec,  
                            'luong_thuviec': luong_thuviec, 
                            'ngay_kyhd': ngay_kyhd,
                            'luong_chinh': rec['luong_chinh'],
                            'luonghopdong': rec['luonghopdong'],
                            'luong_chinh_pd': rec['luong_chinh'],
                            })
                        message_id = self.env['message.wizard'].create({'message':("Tạo đánh giá thử việc thành công.")})
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
                        raise UserError("Nhân viên chưa có user!")
                # Nếu là quản lý đánh giá cho nhân viên
                elif nhansu_tu_danhgia == 'quanlydanhgia':
                    if rec.parent_id and rec.parent_id.nguoikiemnhiem_id:
                        parent_user = rec.get_user_id(rec.parent_id.nguoikiemnhiem_id)
                    elif rec.parent_id:
                        parent_user = rec.get_user_id(rec.parent_id)
                    else:
                        parent_user = False
                    if parent_user:
                        new_dg_thuviec = self.env['hr.dgthuviec'].sudo().create({        
                                'employee_id': rec.id,
                                'user_id': parent_user.id,
                                'ngaykt_thuviec': ngaykt_thuviec,  
                                'luong_thuviec': luong_thuviec, 
                                'ngay_kyhd': ngay_kyhd,
                                'luong_chinh': rec['luong_chinh'],
                                'luonghopdong': rec['luonghopdong'],
                                'luong_chinh_pd': rec['luong_chinh'],
                                })
                        message_id = self.env['message.wizard'].create({'message':("Tạo đánh giá thử việc thành công.")})
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
                        raise UserError("Nhân viên chưa có Quản lý trực tiếp!")
                # Bỏ qua cấp  nhân sự tự đánh giá
                elif nhansu_tu_danhgia == 'boqua':
                    if rec.parent_id and rec.parent_id.nguoikiemnhiem_id:
                        parent_user = rec.get_user_id(rec.parent_id.nguoikiemnhiem_id)
                    elif rec.parent_id:
                        parent_user = rec.get_user_id(rec.parent_id)
                    else:
                        parent_user = False
                    if parent_user:
                        new_dg_thuviec = self.env['hr.dgthuviec'].sudo().create({        
                            'employee_id': rec.id,
                            'user_id': parent_user.id,
                            'ngaykt_thuviec': ngaykt_thuviec,  
                            'luong_thuviec': luong_thuviec, 
                            'ngay_kyhd': ngay_kyhd,
                            'nsdg_xong': True,
                            'tudanhgia': False,
                            'stage_id': self.env.ref('hr_ta.dgthuviec_stage_2').id,
                            'luong_chinh': rec['luong_chinh'],
                            'luonghopdong': rec['luonghopdong'],
                            'luong_chinh_pd': rec['luong_chinh'],
                            })
                        message_id = self.env['message.wizard'].create({'message':("Tạo đánh giá thử việc thành công.")})
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
                        raise UserError("Nhân viên chưa có Quản lý trực tiếp!")
            else:
                raise UserError("Đã tạo Đánh giá thử việc!")
                #rec.sudo().write({"nsdg_xong": True})
                #rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_2').id})
