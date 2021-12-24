# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError


class Tinhcach(models.Model):
    _name = "hr.applicant.tinhcach"
    _description = "Tính cách Ứng viên"
    _order = "id desc"
    #_inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
       
    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")       

class TGThuviec(models.Model):
    _name = "hr.tgthuviec"
    _description = "Thời gian thử việc"
    _order = "sequence"
    #_inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
       
    name = fields.Char("Tên", required=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    
    thoigian = fields.Integer(string='Thời gian', required=True)

class PhucapNhanvien(models.Model):
    _name = "hr.applicant.phucap"
    _description = "Phụ cấp theo ứng viên"
    _order = 'sequence'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char("Mô tả", required=True, tracking=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements")
    loaiphucap_id = fields.Many2one('hr.loaiphucap', string='Loại phụ cấp', tracking=True)    
    ma = fields.Char("Mã phụ cấp", related='loaiphucap_id.ma', tracking=True, store=True, readonly=True)
    phucap = fields.Monetary(string='Phụ cấp', tracking=True)
    
    applicant_id = fields.Many2one('hr.applicant', string='Ứng viên', tracking=True)
    currency_id = fields.Many2one('res.currency','Loại tiền', related='applicant_id.currency_id', tracking=True, store=True, readonly=True)
    dgungvien_id = fields.Many2one('hr.dgungvien', string='Đánh giá', tracking=True)

class ApplicantInherit(models.Model):
    _inherit = "hr.applicant"   
    
    nguoituyendung_id = fields.Many2one('res.users',
        string='Người tuyển dụng',
        default=lambda self: self.env.uid,
        tracking=True, store=True, readonly=False)
    department_id = fields.Many2one(
        'hr.department', "Department",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    department_name = fields.Char("Tên Phòng/ Ban", related='department_id.name', store=True, readonly=True)   
    nguoi_pv_id = fields.Many2one('res.users', "Quản lý trực tiếp", compute='_compute_nguoi_pv', tracking=True, store=True, readonly=False)
    manager_id = fields.Many2one('res.users', "Quản lý Phòng/ Ban", compute='_compute_manager', tracking=True, store=True, readonly=False)
    is_self = fields.Boolean("Is self?", compute='_compute_is_self')
    ngay_thumoi = fields.Date('Ngày trên thư mời', tracking=True)
    dgthuviec_id = fields.Many2one('hr.dgthuviec', "Đánh giá thử việc", tracking=True, store=True)
    sosobhxh =  fields.Char("Số sổ BHXH", tracking=True)
    ngaycap_bhxh = fields.Date(string='Ngày cấp BHXH', tracking=True)  
    mst =  fields.Char("Mã số Thuế", tracking=True)
    ngaycap_mst = fields.Date(string='Ngày cấp MST', tracking=True) 
    birthday = fields.Date(string='Ngày sinh', tracking=True) 
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Giới tính", groups="hr.group_hr_user", tracking=True)
    country_id = fields.Many2one(
        'res.country', 'Quốc tịch', tracking=True)
    tongiao_id = fields.Many2one('hr.tongiao', string='Tôn giáo', tracking=True)
    dantoc_id = fields.Many2one('hr.dantoc', string='Dân tộc', tracking=True)
    identification_id = fields.Char(string='CMND/ CCCD', tracking=True)
    noicapcccd_id = fields.Many2one('hr.noicapcccd', string='Nơi cấp', tracking=True)
    ngaycapcccd = fields.Date(string='Ngày cấp', tracking=True)
    passport_id = fields.Char('Hộ chiếu', tracking=True)
    trinhdovh_id = fields.Many2one('hr.trinhdovh', string='Trình độ văn hóa', tracking=True)
    truonghoc_id = fields.Many2one('hr.truonghoc', string='Trường học', tracking=True)
    chuyennganh_id = fields.Many2one('hr.chuyennganh', string='Chuyên ngành', tracking=True)
    honnhan = fields.Selection([
        ('docthan', 'Độc thân'),
        ('dakethon', 'Đã kết hôn'),
        ('lydi', 'Ly dị'),
        ('khac', 'Khác')
    ], string="Tình trạng hôn nhân", tracking=True)
    laynamsinh = fields.Boolean("Lấy năm sinh")
    email_canhan = fields.Char("Email cá nhân", tracking=True)
    sotk =  fields.Char("Số tài khoản", tracking=True)
    tentk =  fields.Char("Tên tài khoản", tracking=True)
    nganhang_id = fields.Many2one('res.bank', string='Ngân hàng', tracking=True)
    address_id = fields.Many2one('res.partner', 'Địa điểm làm việc', tracking=True)   

    def _default_country(self):
        country = self.env["res.country"].sudo().search([("name", "=", "Vietnam")])
        if country:
            for c in country:
                id = c.id
        else:
            id = False
        return id
    # Nơi sinh
    ns_country_id = fields.Many2one('res.country', string='Quốc gia (NS)', default=_default_country, tracking=True)
    ns_state_id = fields.Many2one('res.country.state', string='Tỉnh/ TP (NS)', domain="[('country_id', '=', ns_country_id)]", tracking=True)
    ns_quanhuyen_id = fields.Many2one('res.country.quanhuyen', string='Quận/ Huyện (NS)', domain="[('state_id', '=', ns_state_id)]", tracking=True)
    ns_phuongxa_id = fields.Many2one('res.country.phuongxa', string='Phường/ Xã (NS)', domain="[('quanhuyen_id', '=', ns_quanhuyen_id)]", tracking=True)
    ns_diachi =  fields.Char("Địa chỉ (NS)", tracking=True)
    noisinh =  fields.Char("Nơi sinh", compute='_compute_noisinh', tracking=True, store=True, readonly=True)
    # Quê quán
    qq_country_id = fields.Many2one('res.country', string='Quốc gia (QQ)', default=_default_country, tracking=True)
    qq_state_id = fields.Many2one('res.country.state', string='Tỉnh/ TP (QQ)', domain="[('country_id', '=', qq_country_id)]", tracking=True)
    qq_quanhuyen_id = fields.Many2one('res.country.quanhuyen', string='Quận/ Huyện (QQ)', domain="[('state_id', '=', qq_state_id)]", tracking=True)
    qq_phuongxa_id = fields.Many2one('res.country.phuongxa', string='Phường/ Xã (QQ)', domain="[('quanhuyen_id', '=', qq_quanhuyen_id)]", tracking=True)
    qq_diachi =  fields.Char("Địa chỉ (QQ)", tracking=True)
    quequan =  fields.Char("Quê quán", compute='_compute_quequan', store=True, readonly=True)
    # Thường trú
    tt_country_id = fields.Many2one('res.country', string='Quốc gia (TT)', default=_default_country, tracking=True)
    tt_state_id = fields.Many2one('res.country.state', string='Tỉnh/ TP (TT)', domain="[('country_id', '=', tt_country_id)]", tracking=True)
    tt_quanhuyen_id = fields.Many2one('res.country.quanhuyen', string='Quận/ Huyện (TT)', domain="[('state_id', '=', tt_state_id)]", tracking=True)
    tt_phuongxa_id = fields.Many2one('res.country.phuongxa', string='Phường/ Xã (TT)', domain="[('quanhuyen_id', '=', tt_quanhuyen_id)]", tracking=True)
    tt_diachi =  fields.Char("Địa chỉ (TT)", tracking=True)
    hkthuongtru =  fields.Char("HK Thường trú", compute='_compute_thuongtru', tracking=True, store=True, readonly=True)

    la_choohiennay = fields.Boolean("Là chỗ ở hiện nay", tracking=True)
    # Chỗ ở hiện nay
    co_country_id = fields.Many2one('res.country', string='Quốc gia (COHN)', default=_default_country, tracking=True)
    co_state_id = fields.Many2one('res.country.state', string='Tỉnh/ TP (COHN)', domain="[('country_id', '=', co_country_id)]", tracking=True)
    co_quanhuyen_id = fields.Many2one('res.country.quanhuyen', string='Quận/ Huyện (COHN)', domain="[('state_id', '=', co_state_id)]", tracking=True)
    co_phuongxa_id = fields.Many2one('res.country.phuongxa', string='Phường/ Xã (COHN)', domain="[('quanhuyen_id', '=', co_quanhuyen_id)]", tracking=True)
    co_diachi =  fields.Char("Địa chỉ (COHN)", tracking=True)
    choohiennay =  fields.Char("Chỗ ở hiện nay", compute='_compute_cohiennay', tracking=True, store=True, readonly=True)
   
    pbdg_ketqua = fields.Selection([
        ('dat', 'Đạt (Đề xuất tuyển dụng)'),
        ('khongdat', 'Không đạt')        
    ], string="Kết quả", tracking=True)
    pbdg_ketqua_kdat =  fields.Char("Lý do không đạt", tracking=True)   

    loai_tgthuviec = fields.Selection([
        ('ngay', 'Ngày'),
        ('thang', 'Tháng')        
    ], string="Thử việc theo", default='ngay', tracking=True)

    loai_tgthuviec = fields.Selection([
        ('ngay', 'Ngày'),
        ('thang', 'Tháng')        
    ], string="Thử việc theo", default='ngay', tracking=True)

    tgthuviec_id = fields.Many2one('hr.tgthuviec', string='Thời gian thử việc', tracking=True)

    tg_thuviec = fields.Integer(string='TG thử việc', default=2, tracking=True)
    thuviec_tu = fields.Date('Thử việc từ ngày', tracking=True)
    thuviec_den = fields.Date('Thử việc đến ngày', tracking=True, compute='_compute_thuviecden', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Loại tiền', default=lambda self: self._get_default_currency_id(), required=True, tracking=True)
    luong_chinh = fields.Monetary(string='Lương chính', tracking=True)  
    pt_thuviec = fields.Float(string='Tỷ lệ Lương thử việc', tracking=True, default=85, compute='_compute_tylethuviec', store=True, readonly=False)  
    luong_thuviec = fields.Monetary(string='Lương thử việc', tracking=True, compute='_compute_luongthuviec', store=True, readonly=False) 
    phucap_ids = fields.One2many('hr.applicant.phucap', 'applicant_id', string='Phụ cấp')
    resume_line_ids = fields.One2many('hr.resume.line', 'applicant_id', string="Quá trình đào tạo và làm việc")
    giadinh_ids = fields.One2many('hr.ttgiadinh', 'applicant_id', string='Thông tin gia đình')
    dgungvien_ids = fields.One2many('hr.dgungvien', 'applicant_id', string='Đánh giá')
    soluong_danhgia = fields.Integer(string='Số lượng Đánh giá', compute='_compute_sldanhgia')

    dataodanhgia = fields.Boolean("Đã tạo đánh giá")
    dadanhgia = fields.Boolean("Đã đánh giá")
    dataonhanvien = fields.Boolean("Đã tạo Nhân viên")
    dataohopdong = fields.Boolean("Đã tạo Hợp đồng")

    def _get_default_currency_id(self):
        return self.company_id.currency_id or self.env.company.currency_id    

    @api.depends('write_date')
    def _compute_sldanhgia(self):
        for rec in self:
            if rec['dgungvien_ids']:
                rec['soluong_danhgia'] = len(rec['dgungvien_ids'])
            else:
                rec['soluong_danhgia'] = 0

    #Check my task
    @api.depends('write_date')
    def _compute_is_self(self):
        for rec in self: 
            if(rec['user_id'] == self.env.user):
                rec['is_self'] = True
            else:
                rec['is_self'] = False

    @api.depends('department_id')
    def _compute_nguoi_pv(self):
        for rec in self:
            if rec.department_id:
                rec.nguoi_pv_id = rec.department_id.manager_id.user_id.id
            else:
                rec.nguoi_pv_id = False
    
    @api.depends('department_id')
    def _compute_manager(self):
        for rec in self:
            if rec.department_id:
                rec.manager_id = rec.department_id.manager_id.user_id.id
            else:
                rec.manager_id = False

    @api.depends('luong_chinh', 'pt_thuviec')
    def _compute_luongthuviec(self):
        for rec in self:
            rec.luong_thuviec = rec.luong_chinh * (rec.pt_thuviec/100)

    @api.depends('luong_chinh', 'luong_thuviec')
    def _compute_tylethuviec(self):
        for rec in self:
            if rec['luong_chinh'] > 0:
                rec['pt_thuviec'] = (rec.luong_thuviec * 100)/rec.luong_chinh    

    @api.depends('tgthuviec_id','thuviec_tu')
    def _compute_thuviecden(self):
        for rec in self:
            if rec.tgthuviec_id and rec.thuviec_tu:  
                thogian = rec.tgthuviec_id.thoigian
                rec.thuviec_den = rec.thuviec_tu + timedelta(days=thogian-1)                
            else:
                rec.thuviec_den = False

    @api.depends('ns_country_id', 'ns_state_id', 'ns_quanhuyen_id', 'ns_diachi', 'ns_phuongxa_id')
    def _compute_noisinh(self):
        for rec in self:
            if rec.ns_diachi:
                diachi = rec.ns_diachi + ", "
            else:
                diachi = ""
            if rec.ns_phuongxa_id:
                phuongxa = rec.ns_phuongxa_id.name + ", "
            else:
                phuongxa = ""
            if rec.ns_quanhuyen_id:
                quanhuyen = rec.ns_quanhuyen_id.name + ", "
            else:
                quanhuyen = ""
            if rec.ns_state_id:
                state = rec.ns_state_id.name + ", "
            else:
                state = ""
            if rec.ns_country_id:
                country = rec.ns_country_id.name
            else:
                country = ""
            rec.noisinh = diachi + phuongxa + quanhuyen + state + country

    @api.depends('qq_country_id', 'qq_state_id', 'qq_quanhuyen_id', 'qq_diachi', 'qq_phuongxa_id')
    def _compute_quequan(self):
        for rec in self:
            if rec.qq_diachi:
                diachi = rec.qq_diachi + ", "
            else:
                diachi = ""
            if rec.qq_phuongxa_id:
                phuongxa = rec.qq_phuongxa_id.name + ", "
            else:
                phuongxa = ""
            if rec.qq_quanhuyen_id:
                quanhuyen = rec.qq_quanhuyen_id.name + ", "
            else:
                quanhuyen = ""
            if rec.qq_state_id:
                state = rec.qq_state_id.name + ", "
            else:
                state = ""
            if rec.qq_country_id:
                country = rec.qq_country_id.name
            else:
                country = ""
            rec.quequan = diachi + phuongxa + quanhuyen + state + country

    @api.depends('tt_country_id', 'tt_state_id', 'tt_quanhuyen_id', 'tt_diachi', 'tt_phuongxa_id')
    def _compute_thuongtru(self):
        for rec in self:
            if rec.tt_diachi:
                diachi = rec.tt_diachi + ", "
            else:
                diachi = ""
            if rec.tt_phuongxa_id:
                phuongxa = rec.tt_phuongxa_id.name + ", "
            else:
                phuongxa = ""
            if rec.tt_quanhuyen_id:
                quanhuyen = rec.tt_quanhuyen_id.name + ", "
            else:
                quanhuyen = ""
            if rec.tt_state_id:
                state = rec.tt_state_id.name + ", "
            else:
                state = ""
            if rec.tt_country_id:
                country = rec.tt_country_id.name
            else:
                country = ""
            rec.hkthuongtru = diachi + phuongxa + quanhuyen + state + country

    @api.depends('co_country_id', 'co_state_id', 'co_quanhuyen_id', 'co_diachi', 'co_phuongxa_id', 'tt_country_id', 'tt_state_id', 'tt_quanhuyen_id', 'tt_diachi', 'tt_phuongxa_id', 'la_choohiennay')
    def _compute_cohiennay(self):
        for rec in self:
            if rec['la_choohiennay'] == True:
                rec.co_diachi = rec.tt_diachi
                rec.co_phuongxa_id = rec.tt_phuongxa_id.id
                rec.co_quanhuyen_id = rec.tt_quanhuyen_id.id
                rec.co_state_id = rec.tt_state_id.id
                rec.co_country_id = rec.tt_country_id.id
            if rec.co_diachi:
                diachi = rec.co_diachi + ", "
            else:
                diachi = ""
            if rec.co_phuongxa_id:
                phuongxa = rec.co_phuongxa_id.name + ", "
            else:
                phuongxa = ""
            if rec.co_quanhuyen_id:
                quanhuyen = rec.co_quanhuyen_id.name + ", "
            else:
                quanhuyen = ""
            if rec.co_state_id:
                state = rec.co_state_id.name + ", "
            else:
                state = ""
            if rec.co_country_id:
                country = rec.co_country_id.name
            else:
                country = ""
            rec.choohiennay = diachi + phuongxa + quanhuyen + state + country

    def create_employee(self):       
        for rec in self:
            # Lấy thông tin đánh giá
            dgungvien = self.env["hr.dgungvien"].sudo().search([('applicant_id','=',rec['id']),('stage_id','=',self.env.ref('hr_ta.dgungvien_stage_3').id),('pbdg_ketqua','=','dat')],order='tg_pheduyet desc', limit=1)
            if dgungvien:
                luong_chinh = dgungvien.luong_chinh
                luong_thuviec = dgungvien.luong_thuviec
                thuviec_tu = dgungvien.thuviec_tu
                thuviec_den = dgungvien.thuviec_den            
                # 1. Tạo nhận viên và thông tin
                new_employee = self.env['hr.employee'].sudo().create({
                    'name': rec.name,
                    'department_id': rec.department_id.id,
                    'parent_id': rec.nguoi_pv_id.employee_id.id,
                    'job_id': rec.job_id.id,   
                    'loaihd_id': self.env.ref('hr_employee_contract.hr_contract_type_1').id,
                    'loainv_id': self.env.ref('hr_od.hr_loainv_1').id,
                    'address_id': rec.address_id.id,
                    'ngayvao_tapdoan': rec.thuviec_tu,
                    'ngayvaolam': rec.thuviec_tu,
                    'luong_chinh': luong_chinh,                
                    'work_phone': rec.partner_mobile,
                    'sosobhxh': rec.sosobhxh,
                    'ngaycap_bhxh': rec.ngaycap_bhxh,
                    'mst': rec.mst,
                    'ngaycap_mst': rec.ngaycap_mst,
                    'birthday': rec.birthday,
                    'laynamsinh': rec.laynamsinh,
                    'gender': rec.gender,
                    'country_id': rec.country_id.id,
                    'tongiao_id': rec.tongiao_id.id,
                    'dantoc_id': rec.dantoc_id.id,
                    'honnhan': rec.honnhan,
                    'trinhdovh_id': rec.trinhdovh_id.id,
                    'truonghoc_id': rec.truonghoc_id.id,
                    'chuyennganh_id': rec.chuyennganh_id.id,
                    'identification_id': rec.identification_id,
                    'ngaycapcccd': rec.ngaycapcccd,
                    'noicapcccd_id': rec.noicapcccd_id.id,
                    'passport_id': rec.passport_id,
                    'sotk': rec.sotk,
                    'tentk': rec.tentk,
                    'nganhang_id': rec.nganhang_id.id,
                    'ns_country_id': rec.ns_country_id.id,
                    'ns_state_id': rec.ns_state_id.id,
                    'ns_quanhuyen_id': rec.ns_quanhuyen_id.id,
                    'ns_phuongxa_id': rec.ns_phuongxa_id.id,
                    'ns_diachi': rec.ns_diachi,
                    'noisinh': rec.noisinh,
                    'qq_country_id': rec.qq_country_id.id,
                    'qq_state_id': rec.qq_state_id.id,
                    'qq_quanhuyen_id': rec.qq_quanhuyen_id.id,
                    'qq_phuongxa_id': rec.qq_phuongxa_id.id,
                    'qq_diachi': rec.qq_diachi,
                    'quequan': rec.quequan,
                    'tt_country_id': rec.tt_country_id.id,
                    'tt_state_id': rec.tt_state_id.id,
                    'tt_quanhuyen_id': rec.tt_quanhuyen_id.id,
                    'tt_phuongxa_id': rec.tt_phuongxa_id.id,
                    'tt_diachi': rec.tt_diachi,
                    'hkthuongtru': rec.hkthuongtru,
                    'la_choohiennay': rec.la_choohiennay,
                    'co_country_id': rec.co_country_id.id,
                    'co_state_id': rec.co_state_id.id,
                    'co_quanhuyen_id': rec.co_quanhuyen_id.id,
                    'co_phuongxa_id': rec.co_phuongxa_id.id,
                    'co_diachi': rec.co_diachi,
                    'choohiennay': rec.choohiennay,
                    'nguoituyendung_id': rec.nguoituyendung_id.id,
                })
                rec.emp_id = new_employee
                dgungvien.employee_id = new_employee

                rec.sudo().write({"dataonhanvien": True})
                # 2. Copy thông tin gia đình
                for giadinh in rec.giadinh_ids:
                    giadinh.employee_id = rec.emp_id.id
            
                # 3. Copy lịch sử đào tạo và làm việc từ ứng viên qua nhân viên
                for resume in rec.resume_line_ids:
                    resume.employee_id = rec.emp_id.id
               
                # 6. Tạo hợp đồng thử việc
                new_hd_thuviec = self.env['hr.contract'].sudo().create({                    
                    'employee_id': rec.emp_id.id,
                    'department_id': rec.department_id.id,
                    'job_id': rec.job_id.id,  
                    'company_id': rec.company_id.id,
                    'loaihd_id': self.env.ref('hr_employee_contract.hr_contract_type_1').id,                    
                    'date_start': thuviec_tu,
                    'date_end': thuviec_den,
                    'wage': luong_thuviec,
                    'luonghopdong': luong_thuviec,
                    'address_id': rec.address_id.id,                    
                })
                # 7. Copy phụ cấp từ ứng viên sang Hợp đồng
                if dgungvien['phucap_ids']:
                    for phucap in dgungvien['phucap_ids']:
                        self.env['hr.contract.phucap'].sudo().create({                    
                            'contract_id': new_hd_thuviec.id,
                            'loaiphucap_id': phucap.loaiphucap_id.id,
                            'name': phucap.name,  
                            'phucap': phucap.phucap,                                              
                        })
                rec.sudo().write({"dataohopdong": True})
                message_id = self.env['message.wizard'].create({'message':("Tạo nhân viên thành công.")})
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
                raise UserError("Chưa đánh giá ứng viên")
    def pv_vong1(self):  
        for rec in self:
            rec.sudo().write({"stage_id": self.env.ref('hr_recruitment.stage_job2').id})
    def pv_vong2(self):   
        for rec in self:
            rec.sudo().write({"stage_id": self.env.ref('hr_recruitment.stage_job3').id})
                    
    def daky_hd(self):  
        for rec in self:
            rec.sudo().write({"stage_id": self.env.ref('hr_recruitment.stage_job5').id})

    def tao_dgungvien(self):
        for rec in self:
            dgungvien_search = self.env["hr.dgungvien"].sudo().search([("applicant_id", "=", rec.id),("active", "=", True)])
            if not dgungvien_search:
                self.env['hr.dgungvien'].sudo().create({                    
                    'applicant_id': rec.id,
                    'user_id': rec.nguoituyendung_id.id,
                    'stage_id': self.env.ref('hr_ta.dgungvien_stage_1').id,
                })
                #rec.sudo().write({"dataodanhgia": True})
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
