# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class YeucautuyendungStage(models.Model):
    _name = "hr.yeucautuyendung.stage"
    _description = "Trạng thái yêu cầu Tuyển dụng"
    _order = 'sequence'

    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements")
    template_id = fields.Many2one(
        'mail.template', "Email Template",
        help="If set, a message is posted on the applicant using the template when the applicant is set to the stage.")
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when there are no records in that stage to display.")

class Lydotuyendung(models.Model):
    _name = "hr.yeucautuyendung.lydo"
    _description = "Lý do Tuyển dụng"
    _order = 'sequence'

    name = fields.Char("Lý do", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")

class Loaiyeucau(models.Model):
    _name = "hr.yeucautuyendung.loaiyeucau"
    _description = "Định biên"
    _order = 'sequence'

    name = fields.Char("Định biên", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")

class ViTinh(models.Model):
    _name = "hr.yeucautuyendung.vitinh"
    _description = "Vi tính"
    _order = 'sequence'

    name = fields.Char("Vi tính", required=True)
    color = fields.Integer("Color Index", default=10)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")

class Yeucautuyendung(models.Model):
    _name = "hr.yeucautuyendung"
    _description = "Yêu cầu tuyển dụng"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Yêu cầu", required=True, tracking=True)
    create_date = fields.Datetime("Ngày yêu cầu", readonly=True)
    active = fields.Boolean("Active", default=True)
    description = fields.Text("Nội dung công việc", tracking=True)
    color = fields.Integer("Color Index", default=0)
    stage_id = fields.Many2one('hr.yeucautuyendung.stage', 'Trạng thái', ondelete='restrict',
                               tracking=True, store=True, readonly=False, copy=False, group_expand='_read_group_stage_ids')
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Độ ưu tiên", default='0')
    user_id = fields.Many2one('res.users',
        string='Người xử lý',
        default=lambda self: self.env.uid,
        tracking=True)
    
    is_self = fields.Boolean("Is self?", compute='_compute_is_self')
    company_id = fields.Many2one('res.company', string='Công ty', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Phòng Ban', required=True, tracking=True)
    department_name = fields.Char("Tên Phòng/ Ban", related='department_id.name', store=True, readonly=True)
    #manager_id = fields.Many2one('res.users', "Quản lý Phòng/ Ban", related='department_id.manager_id.user_id', tracking=True, store=True, readonly=True)
    #gd_phutrach = fields.Many2one('res.users', "GĐ Phụ trách", related='department_id.gd_phutrach.user_id', tracking=True, store=True, readonly=True)
    
    job_id = fields.Many2one('hr.job', 'Vị trí tuyển dụng', ondelete='restrict',
                               tracking=True, store=True, required=True, readonly=False, copy=False)
    ngachluong_id = fields.Many2one('hr.ngachluong', 'Ngạch Lương', required=True, ondelete='restrict', compute='_compute_ngachluong', tracking=True, store=True, readonly=False)
    dinhbien = fields.Integer("Định biên", compute='_compute_dinhbien', store=True, readonly=True)
    nhansu_hienco = fields.Integer("Nhân sự hiện có", compute='_compute_nhansuhienco', store=True, readonly=True)

    thoigiancanns = fields.Date(string='Thời gian cần NS', required=True, tracking=True)
    lydo_id = fields.Many2one('hr.yeucautuyendung.lydo', 'Lý do', required=True, ondelete='restrict', tracking=True)
    lydo_khac = fields.Char("Lý do khác", tracking=True)
    color = fields.Integer("Color Index", default=0)
    loaiyeucau_id = fields.Many2one('hr.yeucautuyendung.loaiyeucau', 'Loại yêu cầu', required=True, tracking=True)
    #dinhbien_id = fields.Many2one('hr.yeucautuyendung.loaiyeucau', 'Loại yêu cầu', required=True, tracking=True)
    trinhdovh_id = fields.Many2one('hr.trinhdovh', 'Trình độ học vấn', required=True, tracking=True)    
    soluong = fields.Integer('Số lượng yêu cầu', default=1, required=True, copy=False, tracking=True)
    honnhan = fields.Selection([
        ('docthan', 'Độc thân'),
        ('dalapgiadinh', 'Đã lập gia đình'),
        ('khongquantam', 'Không quan tâm')        
    ], string='Tình trạng hôn nhân', required=True, tracking=True)
    yeucauchung_khac = fields.Text("Yêu cầu khác", tracking=True)
    gioitinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khongquantam', 'Không quan tâm'),
    ], string="Giới tính", required=True, tracking=True)
    congtac = fields.Selection([
        ('nganhan', 'Ngắn hạn'),
        ('daihan', 'Dài hạn'),
        ('theoyeucau', 'Theo yêu cầu')
    ], string="Đi công tác", tracking=True)
    lamviec = fields.Selection([
        ('hanhchanh', 'Giờ hành chánh'),
        ('theoca', 'Theo ca')
    ], string="Làm việc", required=True, tracking=True)
    noilamviec = fields.Selection([
        ('vp', 'VP Công ty'),
        ('nhamay', 'Nhà máy'),
        ('khac', 'Khác')
    ], string="Nơi làm việc", required=True, tracking=True)
    kynang_khac = fields.Text("Kỹ năng yêu cầu khác", tracking=True)
    chuyenmon = fields.Char("Chuyên môn/ Nghiệp vụ", required=True, tracking=True)
    ngoaingu = fields.Char("Ngoại ngữ", required=True, tracking=True)
    vitinh_ids = fields.Many2many('hr.yeucautuyendung.vitinh', string='Vi tính')    
    tuoi_from = fields.Integer('Độ tuổi từ', required=True, tracking=True, default=18)
    tuoi_to = fields.Integer('Độ tuổi đến', required=True, tracking=True, default=18)
    kinhnghiem = fields.Selection([
        ('khong', 'Không cần'),
        ('1nam', '1 năm'),
        ('2nam', '2 năm'),
        ('3nam', '3 năm'),
        ('4nam', '4 năm'),
        ('5nam', '5 năm'),
        ('tren5nam', '>5 năm')
    ], string="Kinh nghiệm", required=True, tracking=True)
    
    manager_dg_xong = fields.Boolean("Quản lý ĐG xong")
    gd_dg_xong = fields.Boolean("GĐ phụ trách ĐG xong")

    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hr.yeucautuyendung.stage'].search([])
    
    @api.model
    def create(self, vals):
        vals['stage_id'] = 1
        result = super(Yeucautuyendung, self).create(vals)
        return result
    
    def unlink(self):
        if any(self.filtered(lambda document: document.stage_id.id in [self.env.ref('hr_ta.yeucautuyendung_stage_4').id,self.env.ref('hr_ta.yeucautuyendung_stage_5').id,self.env.ref('hr_ta.yeucautuyendung_stage_6').id])):
            raise UserError('Không được phép xóa!')
        return super(Yeucautuyendung, self).unlink()

    #Check my task
    @api.depends('write_date')
    def _compute_is_self(self):
        for rec in self: 
            if rec['user_id'] == self.env.user:
                rec.sudo().write({"is_self": True})                
            else:
                rec.sudo().write({"is_self": False}) 

    #Assign to me
    def assign_to_me(self):
        if not self.user_id:
            self.sudo().write({'user_id': self.env.user.id})

    @api.depends('job_id')
    def _compute_ngachluong(self):
        for rec in self:
            if rec['job_id'].ngachluong_id:
                rec['ngachluong_id'] = rec['job_id'].ngachluong_id.id
            else:
                rec['ngachluong_id'] = False

    @api.depends('job_id')
    def _compute_dinhbien(self):
        for rec in self:
            if rec['job_id']:
                rec['dinhbien'] = rec['job_id'].dinhbien
            else:
                rec['dinhbien'] = False
    
    @api.depends('job_id')
    def _compute_nhansuhienco(self):
        for rec in self:
            if rec['job_id']:
                rec['nhansu_hienco'] = rec['job_id'].no_of_employee
            else:
                rec['nhansu_hienco'] = False
                    

    def send_email_pheduyet(self,job,email):
        for rec in self:
            subject = "Phê duyệt yêu cầu tuyển dụng vị trí "+ str(job)
            recipients = email

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            #base_url += '/web#id=%d&action=%d&view_type=list&model=%s' % (self.id, self.env.ref('hr_ta.hr_yeucautuyendung_act').id, self._name)
            body = "Kính gửi: Anh/ Chị "
            body += 'Anh chị có yêu cầu tuyển dụng cần phê duyệt.<br/>'
            body += 'Vị trí tuyển dụng: <b>' + str(job) + '</b><br/>'
            body += 'Anh/ Chị có thể truy cập : ' + "<b><a href="+ base_url + ">TẠI ĐÂY</a></b> để phê duyệt.</br><br/>"
            body += 'Chân thành cảm ơn.<br/>'
            body += 'Hệ thống iPortal - Thuận Hải'
            message_body = body
            template_obj = self.env['mail.mail']
            template_data = {
            'subject': subject,
            'body_html': message_body,
            'email_to': recipients
            }
            template_id = template_obj.create(template_data)
            template_obj.send(template_id)
            template_id.send()           
    
    def send_email_tuchoi(self,lydo,user):
        for rec in self:
            subject = "Yêu cầu tuyển dụng vị trí "+ str(rec.job_id.name) + ' bị từ chối.'
            recipients = rec.create_uid.email  

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            #base_url += '/web#id=%d&action=%d&view_type=form&model=%s' % (self.id, self.env.ref('hr_ta.hr_yeucautuyendung_act').id, self._name)
            body = "Kính gửi: Anh/ Chị "
            body += 'Yêu cầu tuyển dụng của anh chị bị từ chối.<br/>'
            body += 'Vị trí tuyển dụng: <b>' + str(rec.job_id.name) + '</b><br/>'
            body += 'Lý do: ' + str(lydo)
            body += 'Anh/ Chị có thể truy cập : ' + "<b><a href="+ base_url + ">TẠI ĐÂY</a></b> để xem chi tiết.</br><br/>"
            body += 'Chân thành cảm ơn.<br/>'
            body += 'Hệ thống iPortal - Thuận Hải'
            
            message_body = body
            template_obj = self.env['mail.mail']
            
            template_data = {
            'subject': subject,
            'body_html': message_body,
            'email_to': recipients
            }
            template_id = template_obj.create(template_data)
            template_obj.send(template_id)
            template_id.send()

            self.env['mail.message'].create({
                'subject': subject,
                'model': self._name,
                'author_id': user.partner_id.id,
                'date': datetime.now(),
                'message_type': 'comment',                
                'res_id': self.id,
                'record_name': self.name,
                'body': body
              })

    def get_manager(self,department):        
        if department.manager_id.nguoikiemnhiem_id:
            manager_user = self.env["res.users"].sudo().search([('employee_id','=',department.manager_id.nguoikiemnhiem_id.id)]) 
            manager = manager_user
        else:
            manager = department.manager_id.user_id            
        return manager

    def get_gd_phutrach(self,department):        
        if department.gd_phutrach_id.nguoikiemnhiem_id:
            gdphutrach_user = self.env["res.users"].sudo().search([('employee_id','=',department.gd_phutrach_id.nguoikiemnhiem_id.id)]) 
            gd_phutrach = gdphutrach_user    
        else:
            gd_phutrach = department.gd_phutrach_id.user_id
        return gd_phutrach

    def submit(self):
        for rec in self:
            if rec['stage_id'].id == self.env.ref('hr_ta.yeucautuyendung_stage_1').id:    
                nhansu_hienco = self.env["hr.employee"].sudo().search_count([('active','=',True),('job_id','=',rec['job_id'].id)]) 
                if ((nhansu_hienco + rec['soluong']) > rec['job_id'].dinhbien and rec['soluong'] <= rec['job_id'].dinhbien and rec.lydo_id.id == self.env.ref('hr_ta.yeucautuyendung_lydo_1').id) or (nhansu_hienco + rec['soluong']) <= rec['job_id'].dinhbien:
                    manager = rec.get_manager(rec['department_id'])
                    gd_phutrach = rec.get_gd_phutrach(rec['department_id'])
                    if manager and gd_phutrach:
                        if (manager.id == rec['user_id'].id) and (rec['loaiyeucau_id'].id == self.env.ref('hr_ta.yeucautuyendung_loaiyeucau_1').id):
                            self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_4').id})
                            self.sudo().write({"user_id": False})
                            self.sudo().write({"manager_dg_xong": True})   
                            self.job_id.sudo().write({"state": 'recruit'})
                        elif (manager.id == rec['user_id'].id) and (rec['loaiyeucau_id'].id == self.env.ref('hr_ta.yeucautuyendung_loaiyeucau_2').id):
                            self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_3').id})
                            self.sudo().write({"user_id": gd_phutrach.id})
                            self.sudo().write({"manager_dg_xong": True})
                            #rec.send_email_pheduyet(rec['job_id'].name,gd_phutrach.email)
                        else:
                            self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_2').id})
                            self.sudo().write({"user_id": manager.id})
                            #rec.send_email_pheduyet(rec['job_id'].name,manager.email)
                    else:
                        UserError("Phòng/ Ban chưa có Quản lý hoặc GĐ Phụ trách!")
                else:
                    raise UserError("Yêu cầu tuyển dụng vượt quá định biên! Vui lòng liên hệ Phòng HCNS để được hướng dẫn!")

    def quanly_approve(self):
        for rec in self:
            manager = rec.get_manager(rec['department_id'])
            gd_phutrach = rec.get_gd_phutrach(rec['department_id'])
            if rec['loaiyeucau_id'].id == self.env.ref('hr_ta.yeucautuyendung_loaiyeucau_1').id:
                self.sudo().write({"manager_dg_xong": True})
                self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_4').id})
                self.job_id.sudo().write({"state": 'recruit'})
                self.sudo().write({"user_id": False})
            elif rec['loaiyeucau_id'].id == self.env.ref('hr_ta.yeucautuyendung_loaiyeucau_2').id:
                self.sudo().write({"manager_dg_xong": True})
                self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_3').id})                
                self.sudo().write({"user_id": gd_phutrach.id})

    def bod_approve(self):
        for rec in self:
            manager = rec.get_manager(rec['department_id'])
            gd_phutrach = rec.get_gd_phutrach(rec['department_id'])            
            if rec['stage_id'].id == self.env.ref('hr_ta.yeucautuyendung_stage_3').id and rec['manager_dg_xong'] == True:
                self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_4').id})
                self.job_id.sudo().write({"state": 'recruit'})
                #self.job_id.state = 'recruit'
                self.sudo().write({"gd_dg_xong": True})
                self.sudo().write({"user_id": False})
                
    def reject(self):
        for rec in self:
            #if rec['stage_id'].id == self.env.ref('hr_ta.yeucautuyendung_stage_2').id:
            self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_1').id})  
            self.sudo().write({"user_id": rec['create_uid']})
                
    def complete(self):
        self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_5').id})
        #self.job_id.state = 'open'
        self.job_id.sudo().write({"state": 'open'})

    def cancel(self):
        self.sudo().write({"active": False}) 
        self.sudo().write({"stage_id": self.env.ref('hr_ta.yeucautuyendung_stage_6').id})