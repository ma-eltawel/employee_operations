from markupsafe import Markup
from odoo import fields, models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'HR Employee'

    task_count = fields.Integer(compute='compute_task_count')
    late_task_count = fields.Integer(compute='_compute_late_task_count')
    request_count = fields.Integer(compute='_compute_request_count')
    task_ids = fields.One2many('employee.task', 'employee_id')

    def compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    def _compute_late_task_count(self):
        for rec in self:
            rec.late_task_count = self.env['employee.task'].search_count([
                ('employee_id', '=', rec.id),
                ('is_late', '=', True)
            ])

    def _compute_request_count(self):
        for rec in self:
            rec.request_count = self.env['internal.sale.request'].search_count([('employee_id', '=', rec.id)])

    def action_open_task(self):
        self.ensure_one()
        return {
            'name': 'Employee Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'employee.task',
            'domain': [('employee_id', '=', self.id)]
        }

    def action_open_late_task(self):
        self.ensure_one()
        return {
            'name': 'Late Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'employee.task',
            'target': 'new',
            'domain': [
                ('employee_id', '=', self.id),
                ('is_late', '=', True)
            ]
        }

    def action_open_request(self):
        return {
            'name': 'Employee Requests',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'internal.sale.request',
            'domain': [('employee_id', '=', self.id)]
        }

    @api.model
    def monthly_scheduled_job(self):
        first_day = fields.Date.today().replace(day=1)
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            task_count = self.env['employee.task'].search_count([
                ('employee_id', '=', employee.id),
                ('create_date', '>=', first_day)
            ])
            request_count = self.env['internal.sale.request'].search_count([
                ('employee_id', '=', employee.id),
                ('create_date', '>=', first_day)
            ])
            message = Markup(f"""
                    <b>Monthly Summary ({first_day.strftime('%B %Y')})</b>
                    <ul>
                        <li>Tasks created: <b>{task_count}</b></li>
                        <li>Sales Requests: <b>{request_count}</b></li>
                    </ul>
                """)
            employee.message_post(
                body=message,
                subtype_xmlid="mail.mt_comment"
            )