
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import UserError

class ApplicantGetRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'
    
    def action_refuse_reason_apply(self):
        return self.applicant_ids.write({
            'refuse_reason_id': self.refuse_reason_id.id,
            'active': False,
            'stage_id': self.env.ref('hr_ta.hr_applicant_stage_job5').id,
            })