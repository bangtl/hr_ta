# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from openerp.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class DGThuviecStage(models.Model):
    _name = "hr.dgthuviec.stage"
    _description = "Trạng thái Đánh giá thử việc"
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

class KHThuviecStage(models.Model):
    _name = "hr.khthuviec.stage"
    _description = "Trạng thái Đánh giá thử việc"
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

class Pheduyetcuoi(models.Model):
    _name = "hr.dgthuviec.pheduyetcuoi"
    _description = "Phê duyệt cuối"
    _order = 'sequence'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements")    
    active = fields.Boolean("Active", default=True)
    default = fields.Boolean("Default")
    
    company_id = fields.Many2one('res.company', string='Công ty')
    user_id = fields.Many2one('res.users', string='User')

class KehoachCongviec(models.Model):
    _name = "hr.khcongviec"
    _description = "Kế hoạch công việc"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Công việc", required=True, tracking=True)   
    description = fields.Text("Nội dung công việc", tracking=True)   
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Độ ưu tiên", default='0', tracking=True)    
    tungay = fields.Date(string='Từ ngày', tracking=True)
    denngay = fields.Date(string='Đến ngày', tracking=True)

    khthuviec_id = fields.Many2one('hr.khthuviec', string='Kế hoạch thử việc', tracking=True, ondelete='cascade')
    
    ketqua = fields.Char("Kết quả", tracking=True)
    danhgia = fields.Integer("Đánh giá (%)", default=0, tracking=True)
    nguoi_hotro_id = fields.Many2one('hr.employee', string='Người hỗ trợ', tracking=True)

class CongviecThucte(models.Model):
    _name = "hr.cvthucte"
    _description = "Công việc thực tế"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Công việc", required=True, tracking=True)   
    description = fields.Text("Nội dung công việc", tracking=True)   
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Độ ưu tiên", default='0', tracking=True)    
    tungay = fields.Date(string='Từ ngày', tracking=True)
    denngay = fields.Date(string='Đến ngày', tracking=True)

    khthuviec_id = fields.Many2one('hr.khthuviec', string='Kế hoạch thử việc', tracking=True, ondelete='cascade')   
    khthuviec_stage_id = fields.Many2one('hr.khthuviec.stage', 'Trạng thái', related='khthuviec_id.stage_id', store=True)    
    ketqua = fields.Char("Kết quả", tracking=True)
    danhgia = fields.Integer("Đánh giá (%)", default=0, tracking=True)
    nguoi_hotro_id = fields.Many2one('hr.employee', string='Người hỗ trợ', tracking=True)
    loai = fields.Selection([
        ('theokh', 'Theo kế hoạch'),
        ('phatsinh', 'Phát sinh')
    ], string="Loại", required=True, tracking=True)
    ghichu = fields.Char("Ghi chú", tracking=True) 

class Trachnhiemduocgiao(models.Model):
    _name = "hr.dgthuviec.trachnhiem"
    _description = "Trách nhiệm được giao"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Nội dung", required=True, tracking=True)       
    loai = fields.Selection([
        ('trachnhiemchinh', 'Trách nhiệm chính'),
        ('trachnhiemphụ', 'Trách nhiệm phụ')
    ], string="Loại", required=True, tracking=True)
    dgthuviec_id = fields.Many2one('hr.dgthuviec', string='Đánh giá thử việc', tracking=True, ondelete='cascade')

class Quyenhan(models.Model):
    _name = "hr.dgthuviec.quyenhan"
    _description = "Quyền hạn"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Nội dung", required=True, tracking=True)       
    loai = fields.Selection([
        ('tronggioihan', 'Trong giới hạn cho phép'),
        ('ngoaikhanang', 'Ngoài khả năng')
    ], string="Loại", required=True, tracking=True)
    dgthuviec_id = fields.Many2one('hr.dgthuviec', string='Đánh giá thử việc', tracking=True, ondelete='cascade')

class Congviecthuchien(models.Model):
    _name = "hr.dgthuviec.cvthuchien"
    _description = "Công việc thực hiện"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Nội dung", required=True, tracking=True)       
    loai = fields.Selection([
        ('cvchinh', 'Công việc chính'),
        ('cvphu', 'Công việc phụ')
    ], string="Loại", required=True, tracking=True)
    dgthuviec_id = fields.Many2one('hr.dgthuviec', string='Đánh giá thử việc', tracking=True, ondelete='cascade')

class DGThuviecSkill(models.Model):
    _name = "hr.dgthuviec.skill"
    _description = "Skill"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    skill_type_id = fields.Many2one('hr.skill.type', string='Loại', tracking=True)
    skill_id = fields.Many2one('hr.skill', string='Tiêu chí', tracking=True)
    skill_level = fields.Many2one('hr.skill.level', string='Cấp độ', tracking=True)
    danhgia_id = fields.Many2one('hr.skill.danhgia', string='Đánh giá', tracking=True)
    dgthuviec_id = fields.Many2one('hr.dgthuviec', string='Đánh giá thử việc', tracking=True)
    ghichu = fields.Char("Ghi chú", tracking=True) 

class KHThuviec(models.Model):
    _name = "hr.khthuviec"
    _description = "Kế hoạch thử việc"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['hr.khthuviec.stage'].search([], limit=1)   

    is_self = fields.Boolean("Is self?", compute='_compute_is_self')
    name = fields.Char("Tên", compute='_compute_name', store=True, readonly=False)
    create_date = fields.Datetime("Ngày yêu cầu", readonly=True)
    active = fields.Boolean("Active", default=True, tracking=True)
    description = fields.Text("Nội dung công việc", tracking=True)
    color = fields.Integer("Color Index", default=0)

    stage_id = fields.Many2one('hr.khthuviec.stage', 'Trạng thái', ondelete='restrict', default=_default_stage,
                               tracking=True, store=True, readonly=False, copy=False, group_expand='_read_group_stage_ids')
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, tracking=True)    
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Chức danh', store=True, readonly=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Phòng Ban', readonly=True, store=True)    
    company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Công ty', tracking=True, store=True, readonly=True)

    user_id = fields.Many2one('res.users', string='Người xử lý', tracking=True)

    batdau_thuviec = fields.Date(string='Ngày bắt đầu', tracking=True) 
    ketthuc_thuviec = fields.Date(string='Ngày kết thúc', tracking=True)     

    kh_congviec_ids = fields.One2many('hr.khcongviec', 'khthuviec_id', string='Kế hoạch công việc', tracking=True)
    cv_thucte_ids = fields.One2many('hr.cvthucte', 'khthuviec_id', string='Công việc thực tế', tracking=True)
    
    giaoviec_xong = fields.Boolean("Giao việc xong")
    thuviec_xong = fields.Boolean("Thử việc xong")

    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hr.khthuviec.stage'].search([])

    @api.depends('employee_id')
    def _compute_name(self):
        for rec in self:
            if rec['employee_id']:
                rec.name = rec.employee_id.name
            else:
                rec.name = False    

    def get_user_id(self,employee_id):
        user_id = self.env["res.users"].sudo().search([('employee_id','=',employee_id.id)]) 
        if user_id:
            user = user_id
        else:
            user = False         
        return user
    
    # Lấy kế hoạch công viêng sang công việc thực tế
    def copy_kh_congviec(self):  
        for rec in self:
            for kh in rec['kh_congviec_ids']:                
                check_exit = self.env["hr.cvthucte"].sudo().search([("khthuviec_id", "=", rec.id), ("name", "=", kh.name)])
                if not check_exit:
                    self.env['hr.cvthucte'].sudo().create({
                        'khthuviec_id': kh.khthuviec_id.id,
                        'loai': 'theokh',
                        'name': kh.name,
                        'description': kh.description,
                        'tungay': kh.tungay,
                        'denngay': kh.denngay,
                        'nguoi_hotro_id': kh.nguoi_hotro_id.id
                    })
    def get_user_id(self,employee):
        user = False
        if employee:
            user_id = self.env["res.users"].sudo().search([('employee_id','=',employee.id)]) 
            if user_id:
                user = user_id                     
        return user

    def giaoviec(self):  
        for rec in self:
            if rec['employee_id']:
                if len(rec['kh_congviec_ids']) > 0:
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_2').id})
                    rec.sudo().write({"giaoviec_xong": True})
                    if rec['employee_id'].user_id:
                        rec.sudo().write({"user_id": rec['employee_id'].user_id.id})
                    else:
                        raise UserError("Nhân viên chưa có user!")
                else:
                    raise UserError("Vui lòng nhập kế hoạch công việc!")
            else:
                raise UserError("Chưa có nhân sự!")

    def thuviec(self):  
        for rec in self:
            if len(rec['cv_thucte_ids']) > 0:
                # Lấy user của người quản lý trực tiếp
                if rec.employee_id.parent_id and rec.employee_id.parent_id.nguoikiemnhiem_id:
                    parent_user = rec.get_user_id(rec.employee_id.parent_id.nguoikiemnhiem_id)
                elif rec.employee_id.parent_id:
                    parent_user = rec.get_user_id(rec.employee_id.parent_id)
                else:
                    parent_user = False
                rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_3').id})
                rec.sudo().write({"thuviec_xong": True})
                if parent_user:
                    rec.sudo().write({"user_id": parent_user.id})
                else:
                    raise UserError("Nhân viên chưa có quản lý trực tiếp!")
            else:
                raise UserError("Vui lòng nhập công việc đã thực hiện!")

    def qltructiep(self):  
        for rec in self:   
            dg = False
            for cv_thucte in rec['cv_thucte_ids']:
                if cv_thucte.danhgia > 0: 
                    dg = True
                else:
                    dg = False
                    break
            if dg == True:   
                # Lấy user quản lý Phòng/ Ban
                if rec.employee_id.department_id.manager_id and rec.employee_id.department_id.manager_id.nguoikiemnhiem_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.manager_id.nguoikiemnhiem_id)
                elif rec.employee_id.department_id.manager_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.manager_id)
                else:
                    manager_user = False

                if manager_user and manager_user.id == rec['user_id'].id:
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_5').id})                  
                elif manager_user and manager_user.id != rec['user_id'].id and rec.employee_id.id == rec.employee_id.department_id.manager_id.id:
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_5').id}) 
                elif manager_user and manager_user.id != rec['user_id'].id and rec.employee_id.id != rec.employee_id.department_id.manager_id.id:
                    rec.sudo().write({"user_id": manager_user.id})
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_4').id})  
                else:
                    raise UserError("Chưa có quản lý Phòng/ Ban!")
            else:
                raise UserError("Vui lòng đánh giá công việc thự tế!")
            
    def qlphongban(self):  
        for rec in self:           
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_5').id})   
    
    def huy(self):  
        for rec in self:         
            rec.sudo().write({"active": False}) 
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.khthuviec_stage_6').id})        

class DGThuviec(models.Model):
    _name = "hr.dgthuviec"
    _description = "Đánh giá thử việc"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['hr.dgthuviec.stage'].search([], limit=1)   

    is_self = fields.Boolean("Is self?", compute='_compute_is_self')

    name = fields.Char("Tên", compute='_compute_name', store=True, readonly=False)
    create_date = fields.Datetime("Ngày yêu cầu", readonly=True)
    active = fields.Boolean("Active", default=True, tracking=True)
    description = fields.Text("Nội dung công việc", tracking=True)
    color = fields.Integer("Color Index", default=0)
    stage_id = fields.Many2one('hr.dgthuviec.stage', 'Trạng thái', ondelete='restrict', default=_default_stage,
                               tracking=True, store=True, readonly=False, copy=False, group_expand='_read_group_stage_ids')
    
    tudanhgia = fields.Boolean("Tự đánh giá", default=True, tracking=True)

    priority = fields.Selection(AVAILABLE_PRIORITIES, "Độ ưu tiên", default='0', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, tracking=True)    
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Chức danh', readonly=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Phòng Ban', readonly=True, store=True)
    department_name = fields.Char("Tên Phòng/ Ban", related='department_id.name', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='employee_id.company_id', string='Công ty', tracking=True, store=True, readonly=True)
      
    pheduyetcuoi_id = fields.Many2one('hr.dgthuviec.pheduyetcuoi', string='Cấp phê duyệt cuối', compute='_compute_pheduyetcuoi', tracking=True, store=True, readonly=False)   
        
    skill_ids = fields.One2many('hr.dgthuviec.skill', 'dgthuviec_id', string='Đánh giá', tracking=True)
    user_id = fields.Many2one('res.users',
        string='Người xử lý',
        default=lambda self: self.env.uid,
        tracking=True)
    cacquydinh = fields.Selection([
        ('phuhop', 'Phù hơp'),
        ('khongphuhop', 'Không phù hợp')
    ], string="Các quy định", tracking=True)
    lydo_cacquydinh = fields.Char("Lý do (QĐ)", tracking=True)

    moitruong_lvchung = fields.Selection([
        ('phuhop', 'Phù hơp'),
        ('khongphuhop', 'Không phù hợp')
    ], string="Môi trường làm việc chung", tracking=True)
    lydo_moitruong_lvchung = fields.Char("Lý do (MTC)", tracking=True)

    moitruong_lvrieng = fields.Selection([
        ('phuhop', 'Phù hơp'),
        ('khongphuhop', 'Không phù hợp')
    ], string="Môi trường làm việc Phòng/ Ban", tracking=True)
    lydo_moitruong_lvrieng = fields.Char("Lý do (MTR)", tracking=True)

    qt_cvchung = fields.Selection([
        ('phuhop', 'Phù hơp'),
        ('khongphuhop', 'Không phù hợp')
    ], string="Quy trình công việc chung", tracking=True)
    lydo_qt_cvchung = fields.Char("Lý do(QTC)", tracking=True)

    qt_cvrieng = fields.Selection([
        ('phuhop', 'Phù hơp'),
        ('khongphuhop', 'Không phù hợp')
    ], string="Quy trình công việc Phòng/ Ban", tracking=True)
    lydo_qt_cvrieng = fields.Char("Lý do (QTR)", tracking=True)

    trachnhiem_ids = fields.One2many('hr.dgthuviec.trachnhiem', 'dgthuviec_id', string='Trách nhiệm được giao', tracking=True)
    quyenhan_ids = fields.One2many('hr.dgthuviec.quyenhan', 'dgthuviec_id', string='Quyền hạn', tracking=True)
    ykien_dexuat = fields.Text("Ý kiến/ Đề xuất", tracking=True)
    luachon = fields.Selection([
        ('dongy', 'Đồng ý ký HĐLĐ'),
        ('khongdongy', 'Ngưng hợp tác với cty')        
    ], string="Lựa chọn", tracking=True)
    lydo_luachon =  fields.Char("Lý do (LC)", tracking=True)

    cvthuchien_ids = fields.One2many('hr.dgthuviec.cvthuchien', 'dgthuviec_id', string='Công việc thực hiện', tracking=True)     

    qltructiep_denghi = fields.Selection([
        ('kyhd', 'Ký hợp đồng lao động'),        
        ('chothoiviec', 'Cho thôi việc'),        
        ('thuyenchuyen', 'Thuyên chuyển')
    ], string="Quản lý trực tiếp Đề nghị", tracking=True)    
    
    ngaykt_thuviec = fields.Date(string='Ngày kết thúc thử việc', tracking=True) 
    
    ngay_kyhd = fields.Date(string='Ký HĐ từ ngày', tracking=True)
    ngay_thoiviec = fields.Date(string='Thôi việc từ ngày', tracking=True)    
    phongban_thuyenchuyen_id = fields.Many2one('hr.department', string='Phòng/ Ban mới', tracking=True)
    vitri_thuyenchuyen_id = fields.Many2one('hr.job', string='Vị trí mới', tracking=True)

    currency_id = fields.Many2one('res.currency', string='Loại tiền', default=lambda self: self._get_default_currency_id(), required=True, tracking=True)

    luong_thuviec = fields.Monetary(string='Lương thử việc', tracking=True)
    luong_chinh = fields.Monetary(string='Lương chính', tracking=True) 
    luonghopdong = fields.Monetary(string='Lương HĐ', tracking=True) 
    
    luong_chinh_pd = fields.Monetary(string='Lương chính ký HĐ', compute='_compute_luong_chinh_pd', tracking=True, store=True, readonly=False) 
    luong_hd_pd = fields.Monetary(string='Lương HĐ', tracking=True) 
    
    nsdg_xong = fields.Boolean("Nhân sự tự đánh giá")
    qldg_xong = fields.Boolean("Quản lý trực tiếp đánh giá")
    tpdg_xong = fields.Boolean("Trưởng phòng đánh giá")

    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hr.dgthuviec.stage'].search([])

    def _get_default_currency_id(self):
        return self.company_id.currency_id or self.env.company.currency_id   

    #def unlink(self):
    #    if any(self.filtered(lambda document: document.stage_id.id == self.env.ref('hr_ta.dgthuviec_stage_5').id or document.stage_id.id == self.env.ref('dgthuviec_stage_6').id)):
    #        raise UserError('Không được phép xóa đánh giá!')
    #    return super(DGThuviec, self).unlink()

    #Check my task
    @api.depends('write_date')
    def _compute_is_self(self):
        for rec in self: 
            if rec['user_id'] == self.env.user:
                rec.sudo().write({"is_self": True})                
            else:
                rec.sudo().write({"is_self": False})  

    @api.depends('employee_id')
    def _compute_name(self):
        for rec in self:
            if rec['employee_id']:
                rec.name = rec.employee_id.name
            else:
                rec.name = False            
    @api.depends('employee_id')
    def _compute_pheduyetcuoi(self): 
        for rec in self:
            if rec['employee_id']:
                cap_pheduyetcuoi = self.env["hr.dgthuviec.pheduyetcuoi"].sudo().search([('active','=',True),('default','=',True),('company_id','=',self.company_id.id)],order='sequence asc', limit=1) 
                if cap_pheduyetcuoi:
                    pheduyet = cap_pheduyetcuoi.id
                else:
                    pheduyet = False
            else:
                 pheduyet = False
            rec['pheduyetcuoi_id'] = pheduyet      
                
    @api.depends('employee_id','qltructiep_denghi')
    def _compute_luong_chinh_pd(self):
        for rec in self:            
            if rec['employee_id'] and rec['qltructiep_denghi'] != 'chothoiviec':                
                rec.luong_chinh_pd = rec['employee_id'].luong_chinh
            else:
                rec.luong_chinh_pd = 0

    def get_user_id(self,employee):
        user = False
        if employee:
            user_id = self.env["res.users"].sudo().search([('employee_id','=',employee.id)]) 
            if user_id:
                user = user_id                     
        return user

    def nsdg(self):  
        for rec in self:
            if rec.employee_id.parent_id:
                # Lấy user của người quản lý trực tiếp
                if rec.employee_id.parent_id.nguoikiemnhiem_id:
                    parent_user = rec.get_user_id(rec.employee_id.parent_id.nguoikiemnhiem_id)
                else:
                    parent_user = rec.get_user_id(rec.employee_id.parent_id)
                
                if len(rec['trachnhiem_ids']) > 0 and len(rec['quyenhan_ids']) > 0:
                    rec.sudo().write({"nsdg_xong": True})
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_2').id})
                    rec.sudo().write({"user_id": parent_user.id})
                else:
                    raise UserError("Vui lòng nhập trách nhiệm và quyền hạn!")
            else:
                raise UserError("Nhân viên chưa có quản lý trực tiếp!")
    
    def qldg(self):  
        for rec in self:
            dg = False
            for skill in rec['skill_ids']:
                if skill.danhgia_id: 
                    dg = True
                else:
                    dg = False
                    break
            if len(rec['skill_ids']) > 0 and dg == True:
                # Lấy user quản lý Phòng/ Ban
                if rec.employee_id.department_id.pheduyet_dgthuviec_id and rec.employee_id.department_id.pheduyet_dgthuviec_id.nguoikiemnhiem_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.pheduyet_dgthuviec_id.nguoikiemnhiem_id)
                elif rec.employee_id.department_id.pheduyet_dgthuviec_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.pheduyet_dgthuviec_id)
                elif rec.employee_id.department_id.manager_id and rec.employee_id.department_id.manager_id.nguoikiemnhiem_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.manager_id.nguoikiemnhiem_id)
                elif rec.employee_id.department_id.manager_id:
                    manager_user = rec.get_user_id(rec.employee_id.department_id.manager_id)
                else:
                    manager_user = False   
                    
                if manager_user and manager_user.id == rec.user_id.id:
                    rec.sudo().write({"qldg_xong": True})   
                    rec.tpdg() 
                elif manager_user and manager_user.id != rec.user_id.id and rec.employee_id.id == rec.employee_id.department_id.manager_id.id:
                    rec.sudo().write({"qldg_xong": True})   
                    rec.tpdg()
                elif manager_user and manager_user.id != rec.user_id.id and rec.employee_id.id != rec.employee_id.department_id.manager_id.id:
                    rec.sudo().write({"qldg_xong": True})
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_3').id})
                    rec.sudo().write({"user_id": manager_user.id})                
            else:
                raise UserError("Vui lòng nhận xét và đánh giá theo 3 tiêu chí!")
            
    def tpdg(self):  
        for rec in self: 
            if rec.qltructiep_denghi == 'kyhd' or rec.qltructiep_denghi == 'thuyenchuyen':
                if rec.luong_chinh_pd > 0:
                    if rec.pheduyetcuoi_id.user_id and rec.pheduyetcuoi_id.user_id.id == rec.user_id.id:
                        rec.sudo().write({"tpdg_xong": True})
                        rec.approve()
                    elif rec.pheduyetcuoi_id.user_id and rec.pheduyetcuoi_id.user_id.id != rec.user_id.id:  
                        rec.sudo().write({"tpdg_xong": True})
                        rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_4').id})
                        rec.sudo().write({"user_id": rec.pheduyetcuoi_id.user_id.id})
                    else:
                        raise UserError("Không có cấp phê duyệt cuối!") 
                else:
                    raise UserError("Vui lòng nhập mức lương ký hợp đồng!")
            else:
                if rec.pheduyetcuoi_id.user_id and rec.pheduyetcuoi_id.user_id.id == rec.user_id.id:
                    rec.sudo().write({"tpdg_xong": True})
                    rec.approve()
                elif rec.pheduyetcuoi_id.user_id and rec.pheduyetcuoi_id.user_id.id != rec.user_id.id:  
                    rec.sudo().write({"tpdg_xong": True})
                    rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_4').id})
                    rec.sudo().write({"user_id": rec.pheduyetcuoi_id.user_id.id})
                else:
                    raise UserError("Không có cấp phê duyệt cuối!")

    def approve(self): 
        for rec in self:
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_5').id})
            #Đồng ý ký hợp đồng chính thức
            if rec.qltructiep_denghi == 'kyhd':
                 # Tạo hợp đồng
                 new_hd_chinhthuc = self.env['hr.contract'].sudo().create({                    
                        'employee_id': rec.employee_id.id,
                        'department_id': rec.department_id.id,
                        'job_id': rec.job_id.id,  
                        'company_id': rec.company_id.id,
                        'loaihd_id': self.env.ref('hr_employee_contract.hr_contract_type_2').id,
                        'date_start': rec.ngay_kyhd,   
                        'ngachluong_id': rec.employee_id.ngachluong_id.id,
                        'bacluong_id': rec.employee_id.bacluong_id.id,
                        'wage': rec.luong_chinh_pd,
                        'luonghopdong': rec.luong_hd_pd,
                        'address_id': rec.employee_id.address_id.id,                    
                    })

                 # Kiểm tra phụ cấp
                 contract = self.env["hr.contract"].sudo().search([("employee_id", "=", rec.employee_id.id), ('loaihd_id', '=', self.env.ref('hr_employee_contract.hr_contract_type_1').id)])
                 if contract:
                    for cont in contract:
                        if len(cont.phucap_ids) > 0:                            
                            for phucap in cont.phucap_ids:
                                self.env['hr.contract.phucap'].sudo().create({                    
                                    'contract_id': new_hd_chinhthuc.id,
                                    'loaiphucap_id': phucap.loaiphucap_id.id,
                                    'name': phucap.name,  
                                    'phucap': phucap.phucap,                                              
                                })
            #Thuyên chuyển sang vị trí mới
            elif rec.qltructiep_denghi == 'thuyenchuyen':
                #tạo hợp đồng
                new_hd_chinhthuc = self.env['hr.contract'].sudo().create({                    
                        'employee_id': rec.employee_id.id,
                        'department_id': rec.phongban_thuyenchuyen_id.id,
                        'job_id': rec.vitri_thuyenchuyen_id.id,  
                        'company_id': rec.company_id.id,
                        'loaihd_id': self.env.ref('hr_employee_contract.hr_contract_type_2').id,
                        'date_start': rec.ngay_kyhd,   
                        'ngachluong_id': rec.employee_id.ngachluong_id.id,
                        'bacluong_id': rec.employee_id.bacluong_id.id,
                        'wage': rec.luong_chinh_pd,
                        'luonghopdong': rec.luong_chinh_pd*(60/100),
                        'address_id': rec.employee_id.address_id.id,                    
                    })

                # Kiểm tra phụ cấp
                contract = self.env["hr.contract"].sudo().search([("employee_id", "=", rec.employee_id.id), ('loaihd_id', '=', self.env.ref('hr_employee_contract.hr_contract_type_1').id)])
                if contract:
                    for cont in contract:
                        if len(cont.phucap_ids) > 0:                            
                            for phucap in cont.phucap_ids:
                                self.env['hr.contract.phucap'].sudo().create({                    
                                    'contract_id': new_hd_chinhthuc.id,
                                    'loaiphucap_id': phucap.loaiphucap_id.id,
                                    'name': phucap.name,  
                                    'phucap': phucap.phucap,                                              
                                })
                #Tạo lệnh thuyên chuyển
                self.env['hr.dieuchuyen'].sudo().create({                    
                        'employee_id': rec.employee_id.id,
                        'phongban_hientai_id': rec.job_id.id,
                        'chucdanh_hientai_id': rec.department_id.id,                        
                        'phongban_moi_id': rec.phongban_thuyenchuyen_id.id,
                        'chucdanh_moi_id': rec.vitri_thuyenchuyen_id.id,                          
                        'ngayhieuluc': rec.ngay_kyhd,
                        'nyc_duyet': True,
                        'pb_duyet': True,
                        'trangthai': 'chopheduyet',                   
                    })
    def cancel(self): 
        for rec in self:
            rec.sudo().write({"active": False}) 
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgthuviec_stage_6').id})
           
    def load_skill(self):
        for rec in self:
            for skill in rec['skill_ids']:
                skill.sudo().unlink()
            for skill in rec.job_id.job_skill_ids:
                self.env['hr.dgthuviec.skill'].sudo().create({
                'dgthuviec_id': rec.id,
                'skill_type_id': skill.skill_type_id.id,
                'skill_id': skill.skill_id.id,                                   
            })

    @api.model
    def create(self, vals):
        dgthuviec = super(DGThuviec, self).create(vals)        
        dgthuviec.load_skill() 
        return dgthuviec      

    def nhacdanhgia(self):           
        #for rec in self:
        ngayhientai = (datetime.utcnow() + timedelta(hours=7)).date()
        #raise UserError(ngayhientai)
        dgthuviec_all = self.env["hr.dgthuviec"].sudo().search([("stage_id", "!=", self.env.ref('hr_ta.dgthuviec_stage_5').id),("stage_id", "!=", self.env.ref('hr_ta.dgthuviec_stage_6').id)])
        #raise UserError(ngayhientai)
        if dgthuviec_all:                 
            for dg in dgthuviec_all:                
                if dg.ngaykt_thuviec and (ngayhientai + timedelta(days=9)) >= dg.ngaykt_thuviec:                    
                    dg.send_email_danhgia()                

    def send_email_danhgia(self):
        for rec in self:
            subject = "Đánh giá thử việc Nhân sự  " + str(rec['employee_id'].name)
            recipients = self.user_id.email

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&action=%d&view_type=form&model=%s' % (self.id, self.env.ref('hr_ta.hr_dgthuviec_act').id, self._name)
                        
            body = "Kính gửi:  Anh/ Chị " + str(rec['user_id'].name) + "<br/>"
            body += "Anh/ Chị vui lòng đánh giá thử việc cho Nhân sự " + rec['employee_id'].name + "<br/>"
            body += 'Anh/ Chị có thể truy cập : ' + "<b><a href="+ base_url + ">TẠI ĐÂY</a></b> để đánh giá.</br><br/>"
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

            odoobot = self.env['res.users'].browse(1)
            self.env['mail.message'].create({
                'subject': subject,
                'model': self._name,
                'author_id': odoobot.partner_id.id,
                'date': datetime.now(),
                'message_type': 'comment',                
                'res_id': self.id,
                'record_name': self.name,
                'body': body
              })
    
    def send_email_tuchoi(self,lydo):
        for rec in self:
            subject = "Từ chối đánh giá thử việc Nhân sự  " + str(rec['employee_id'].name)
            recipients = self.user_id.email

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&action=%d&view_type=form&model=%s' % (self.id, self.env.ref('hr_ta.hr_dgthuviec_act').id, self._name)
                        
            body = "Kính gửi: Anh/ Chị " + str(rec['user_id'].name) + "<br/>"
            body += "Đánh giá thử việc cho Nhân sự " + rec['employee_id'].name + " bị từ chối.<br/>"
            body += 'Lý do từ chối: <b>' + lydo + '</b><br/>'
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

            mess_body = 'Lý do từ chối: <b>' + lydo + '</b>'
            self.env['mail.message'].create({
                'subject': subject,
                'model': self._name,
                'author_id': self.user_id.partner_id.id,
                'date': datetime.now(),
                'message_type': 'comment',                
                'res_id': self.id,
                'record_name': self.name,
                'body': mess_body
              })