# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]

class DGUngvienStage(models.Model):
    _name = "hr.dgungvien.stage"
    _description = "Trạng thái Đánh giá ứng viên"
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
    _name = "hr.dgungvien.pheduyetcuoi"
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

class DGUngvien(models.Model):
    _name = "hr.dgungvien"
    _description = "Đánh giá ứng viên"
    _order = "id desc"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['hr.dgthuviec.stage'].search([], limit=1)

    name = fields.Char("Tên", compute='_compute_name', store=True, readonly=False)
    create_date = fields.Datetime("Ngày yêu cầu", readonly=True)
    active = fields.Boolean("Active", default=True, tracking=True)
    description = fields.Text("Nội dung công việc", tracking=True)
    color = fields.Integer("Color Index", default=0)
    stage_id = fields.Many2one('hr.dgungvien.stage', 'Trạng thái', ondelete='restrict', default=_default_stage,
                               tracking=True, store=True, readonly=False, copy=False, group_expand='_read_group_stage_ids')
    user_id = fields.Many2one('res.users',
        string='Người xử lý',
        default=lambda self: self.env.uid,
        tracking=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Độ ưu tiên", default='0', tracking=True) 

    employee_id = fields.Many2one('hr.employee', string='Nhân viên', tracking=True) 

    applicant_id = fields.Many2one('hr.applicant', string='Ứng viên', tracking=True)          
    job_id = fields.Many2one('hr.job', related='applicant_id.job_id', string='Chức danh', tracking=True, store=True, readonly=True)
    department_id = fields.Many2one('hr.department', related='applicant_id.department_id', string='Phòng Ban', tracking=True, store=True, readonly=True)
    department_name = fields.Char("Tên Phòng/ Ban", related='department_id.name', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='applicant_id.company_id', string='Công ty', tracking=True, store=True, readonly=True)
    nguoi_pv_id = fields.Many2one('res.users', "Người phỏng vấn", related='applicant_id.nguoi_pv_id', tracking=True, store=True, readonly=True)
    manager_id = fields.Many2one('res.users', "Quản lý Phòng/ Ban", related='applicant_id.manager_id', tracking=True, store=True, readonly=True)
    
    is_self = fields.Boolean("Is self?", compute='_compute_is_self')
    #Check my task
    @api.depends('write_date')
    def _compute_is_self(self):
        for rec in self: 
            if rec['user_id'] == self.env.user:
                rec.sudo().write({"is_self": True})                
            else:
                rec.sudo().write({"is_self": False}) 

    tinhcach_ids = fields.Many2many('hr.applicant.tinhcach', string='Tính cách')
    chiuapluc = fields.Selection([
        ('cao', 'Cao'),
        ('trungbinh', 'Trung bình'),
        ('thap', 'Thấp')
    ], string="Khả năng chịu áp lực", tracking=True)
    dienmao_tacphong =  fields.Char("Diện mạo/ Tác phong", tracking=True)    
    giongnoi =  fields.Char("Giọng nói", tracking=True) 
    phuhop_vanhoa =  fields.Char("Mức độ phù hợp VH Cty", tracking=True)
    kt_chuyenmon =  fields.Char("Kiến thức chuyên môn", tracking=True)
    kn_giaotiep =  fields.Char("Kỹ năng giao tiếp", tracking=True)
    trinhbay_diendat =  fields.Char("Trình bày/ Diễn đạt", tracking=True)
    td_ngoaingu =  fields.Char("Trình độ Ngoại ngữ", tracking=True)
    td_vitinh =  fields.Char("Trình độ Vi tính", tracking=True)
    kn_khac =  fields.Char("Kỹ năng khác", tracking=True)
    nsdg_phuhop = fields.Text("Điểm phù hợp (NS)", tracking=True)
    nsdg_hanche = fields.Text("Điểm hạn chế (NS)", tracking=True)
    nsdg_ketluan = fields.Text("Nhân sự Kết luận", tracking=True)
    nsdg_dexuat = fields.Text("Nhân sự Đề xuất", tracking=True)
    
    nsdg_xong = fields.Boolean("Nhân sự đánh giá xong")
    pbdg_xong = fields.Boolean("Phòng/ Ban đánh giá xong")

    pbdg_phuhop = fields.Text("Điểm phù hợp (PB)", tracking=True)
    pbdg_hanche = fields.Text("Điểm hạn chế (PB)", tracking=True)
    pbdg_ketluan = fields.Text("Phòng/ Ban Kết luận", tracking=True)
    pbdg_dexuat = fields.Text("Phòng/ Ban Đề xuất", tracking=True)
    pbdg_ketqua = fields.Selection([
        ('dat', 'Đạt (Đề xuất tuyển dụng)'),
        ('khongdat', 'Không đạt')        
    ], string="Kết quả", tracking=True)
    pbdg_ketqua_kdat =  fields.Char("Lý do không đạt", tracking=True)
    loai_tgthuviec = fields.Selection([
        ('ngay', 'Ngày'),
        ('thang', 'Tháng')   
    ], string="Thử việc theo", default='ngay', tracking=True)

    tgthuviec_id = fields.Many2one('hr.tgthuviec', string='Thời gian thử việc', required=True, tracking=True)

    tg_thuviec = fields.Integer(string='TG thử việc', default=2, tracking=True)
    thuviec_tu = fields.Date('Thử việc từ ngày', tracking=True)
    thuviec_den = fields.Date('Thử việc đến ngày', tracking=True, compute='_compute_thuviecden', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Loại tiền', default=lambda self: self._get_default_currency_id(), required=True, tracking=True)
    #luong_chinh = fields.Monetary(string='Lương chính', compute='_compute_luongchinh', store=True, readonly=False, tracking=True)  
    luong_chinh = fields.Monetary(string='Lương chính', tracking=True)
    pt_thuviec = fields.Float(string='Tỷ lệ Lương thử việc', tracking=True, default=85, compute='_compute_tylethuviec', store=True, readonly=False)  
    luong_thuviec = fields.Monetary(string='Lương thử việc', tracking=True, compute='_compute_luongthuviec', store=True, readonly=False) 
    phucap_ids = fields.One2many('hr.applicant.phucap', 'dgungvien_id', string='Phụ cấp')
    tg_pheduyet = fields.Datetime("Thời gian phê duyệt")
    
    def _get_default_currency_id(self):
        return self.company_id.currency_id or self.env.company.currency_id  

    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['hr.dgungvien.stage'].sudo().search([])

    def unlink(self):
        if any(self.filtered(lambda document: document.stage_id.id == self.env.ref('dgungvien_stage_3').id)):
            raise UserError('Không được phép xóa đánh giá đã được phê duyệt!')
        return super(DGUngvien, self).unlink()

    @api.depends('applicant_id')
    def _compute_name(self):
        for rec in self:
            if rec['applicant_id']:
                rec.name = rec.applicant_id.name
            else:
                rec.name = 0

    @api.depends('pbdg_ketqua')
    def _compute_luongchinh(self):
        for rec in self:
            if rec['pbdg_ketqua'] and rec['pbdg_ketqua'] == 'dat':
                rec['luong_chinh'] = rec.applicant_id.salary_proposed
            else:
                rec['luong_chinh'] = False

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

    def nsdg(self):  
        for rec in self:
            rec.sudo().write({"nsdg_xong": True})
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_2').id})
            rec.sudo().write({"user_id": rec['nguoi_pv_id'].id})

    def pbdg(self):  
        for rec in self:
            rec.sudo().write({"pbdg_xong": True})
            rec.applicant_id.sudo().write({"pbdg_ketqua": rec.pbdg_ketqua}) 
            if rec.pbdg_ketqua == 'dat':  
                if rec['manager_id'] == rec.user_id:
                    rec.approve()
                else:
                    rec.sudo().write({"user_id": rec['manager_id'].id})
            else:
                rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_3').id})
                #rec.sudo().write({"user_id": rec['applicant_id'].nguoituyendung_id.id})            
                rec.applicant_id.sudo().write({"dadanhgia": True}) 
                rec.applicant_id.sudo().write({"pbdg_ketqua_kdat": rec.pbdg_ketqua_kdat})             
    
    def approve(self): 
        for rec in self:      
            pheduyetcuoi = self.env["hr.dgungvien.pheduyetcuoi"].sudo().search([("company_id", "=", rec.company_id.id),("active", "=", True)], limit=1)
            if pheduyetcuoi:
                rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_5').id})               
                rec.sudo().write({"user_id": pheduyetcuoi.user_id.id})
            else:
                if rec.pbdg_ketqua == 'dat':
                    rec.applicant_id.sudo().write({"stage_id": self.env.ref('hr_recruitment.stage_job4').id})
                    rec.applicant_id.sudo().write({"tgthuviec_id": rec.tgthuviec_id.id}) 
                    rec.applicant_id.sudo().write({"thuviec_tu": rec.thuviec_tu}) 
                    rec.applicant_id.sudo().write({"thuviec_den": rec.thuviec_den}) 
                    rec.applicant_id.sudo().write({"luong_chinh": rec.luong_chinh})
                    rec.applicant_id.sudo().write({"pt_thuviec": rec.pt_thuviec})
                    rec.applicant_id.sudo().write({"luong_thuviec": rec.luong_thuviec})
                    phucap = self.env["hr.applicant.phucap"].sudo().search([('applicant_id','=',rec.applicant_id.id)])
                    if phucap:
                        for pc in phucap:
                            pc.sudo().unlink()
                    for pc in rec.phucap_ids:
                        self.env['hr.applicant.phucap'].sudo().create({                    
                            'name': pc.name,
                            'loaiphucap_id': pc.loaiphucap_id.id,
                            'phucap': pc.phucap,  
                            'applicant_id': rec.applicant_id.id,                                      
                    })
                rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_3').id})
                rec.applicant_id.sudo().write({"dadanhgia": True}) 
                rec.sudo().write({"user_id": rec['applicant_id'].nguoituyendung_id.id})
            
    def hcns_approve(self): 
        for rec in self:            
            if rec.pbdg_ketqua == 'dat':
                rec.applicant_id.sudo().write({"stage_id": self.env.ref('hr_recruitment.stage_job4').id})
                rec.applicant_id.sudo().write({"tgthuviec_id": rec.tgthuviec_id.id}) 
                rec.applicant_id.sudo().write({"thuviec_tu": rec.thuviec_tu}) 
                rec.applicant_id.sudo().write({"thuviec_den": rec.thuviec_den}) 
                rec.applicant_id.sudo().write({"luong_chinh": rec.luong_chinh})
                rec.applicant_id.sudo().write({"pt_thuviec": rec.pt_thuviec})
                rec.applicant_id.sudo().write({"luong_thuviec": rec.luong_thuviec})
                phucap = self.env["hr.applicant.phucap"].sudo().search([('applicant_id','=',rec.applicant_id.id)])
                if phucap:
                    for pc in phucap:
                        pc.sudo().unlink()
                for pc in rec.phucap_ids:
                    self.env['hr.applicant.phucap'].sudo().create({                    
                        'name': pc.name,
                        'loaiphucap_id': pc.loaiphucap_id.id,
                        'phucap': pc.phucap,  
                        'applicant_id': rec.applicant_id.id,                                      
                })
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_3').id})
            rec.applicant_id.sudo().write({"dadanhgia": True}) 
            rec.sudo().write({"user_id": rec['applicant_id'].nguoituyendung_id.id})   

    def huy(self):  
        for rec in self:
            rec.sudo().write({"active": False})
            rec.sudo().write({"stage_id": self.env.ref('hr_ta.dgungvien_stage_4').id})
