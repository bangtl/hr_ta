# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError


class Danhgia(models.Model):
    _name = 'hr.skill.danhgia'
    _description = "Đánh giá"

    name = fields.Char(required=True)
    skill_type_id = fields.Many2one('hr.skill.type', ondelete='cascade')
    active = fields.Boolean("Active", default=True)

class SkillTypeInherit(models.Model):
    _inherit = "hr.skill.type" 

    danhgia_ids = fields.One2many('hr.skill.danhgia', 'skill_type_id', string="Đánh giá")

class SkillInherit(models.Model):
    _inherit = "hr.skill" 

    default = fields.Boolean("Mặc định")