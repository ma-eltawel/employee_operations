from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'HR Employee'

    task_count = fields.Integer(compute='compute_task_count')
    late_task_count = fields.Integer(compute='_compute_late_task_count')
    request_count = fields.Integer(compute='_compute_request_count')
    task_ids = fields.One2many('employee.task', 'employee_id')

    def compute_task_count(self):
        for rec in self:
            rec.task_count = self.env['employee.task'].search_count([('employee_id', '=', rec.id)])

    def _compute_late_task_count(self):
        for rec in self:
            rec.late_task_count = self.env['employee.task'].search_count([
                ('employee_id', '=', rec.id),
                ('is_late', '=', 1)
            ])

    def _compute_request_count(self):
        for rec in self:
            rec.request_count = self.env['internal.sale.request'].search_count([('employee_id', '=', rec.id)])

    def action_open_employee_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Tasks',
            'res_model': 'employee.task.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }