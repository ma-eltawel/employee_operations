from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    task_count = fields.Integer(compute='compute_task_count')
    late_task_count = fields.Integer(compute='_compute_late_task_count')
    request_count = fields.Integer(compute='_compute_request_count')

    @api.depends('task_count')
    def compute_task_count(self):
        for rec in self:
            rec.task_count = 0

    @api.depends('late_task_count')
    def _compute_late_task_count(self):
        for rec in self:
            rec.late_task_count = 0

    @api.depends('request_count')
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = 0