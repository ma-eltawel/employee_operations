from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.orm.decorators import readonly


class EmployeeTask(models.Model):
    _name = 'employee.task'
    _description = 'Employee Task Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=1)
    employee_id = fields.Many2one('hr.employee', required=1)
    description = fields.Text()
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ])
    task_type = fields.Selection([
        ('operational', 'Operational'),
        ('administrative', 'Administrative'),
        ('sales', 'Sales')
    ])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], default='draft')
    deadline = fields.Date(default=fields.Date.today())
    estimated_hours = fields.Float()
    actual_hours = fields.Float()
    progress = fields.Integer(compute='_compute_progress')
    is_late = fields.Boolean(compute='_compute_is_late', store=1)
    parent_task_id = fields.Many2one('employee.task', readonly=1, ondelete='cascade')
    child_task_ids = fields.One2many('employee.task', 'parent_task_id')
    company_id = fields.Many2one('res.company')


    @api.depends('estimated_hours', 'actual_hours')
    def _compute_progress(self):
        for rec in self:
            rec.progress = (rec.actual_hours / rec.estimated_hours) * 100 if rec.estimated_hours else 0.0

    @api.depends('state', 'deadline')
    def _compute_is_late(self):
        for rec in self:
            rec.is_late = rec.deadline < fields.Date.today() and rec.state != 'done'

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if rec.actual_hours < 1:
                raise ValidationError('Actual hours cannot be less than 1!')
            if rec.parent_task_id:
                if all(t.state == 'done' for t in rec.parent_task_id.child_task_ids):
                    rec.parent_task_id.state = 'done'
            rec.state = 'done'

    def action_canceled(self):
        for rec in self:
            rec.state = 'canceled'

    # @api.depends('child_task_ids.state')
    # def _check_parent_done(self):
    #     for rec in self:
    #         if rec.state == 'in_progress' and rec.child_task_ids and all(child.state == 'done' for child in rec.child_task_ids):
    #             rec.state = 'done'
    #
    # def write(self, vals):
    #     res = super(EmployeeTask, self).write(vals)
    #     for rec in self:
    #         if rec.parent_task_id and rec.parent_task_id.state == 'in_progress':
    #             parent = rec.parent_task_id
    #             if parent.child_task_ids and all(c.state == 'done' for c in parent.child_task_ids):
    #                 parent.state = 'done'
    #     return res

    def daily_scheduled_job(self):
        late_tasks = self.search([('is_late', '=', 1)])
        for task in late_tasks:
            manager = task.employee_id.parent_id
            if manager and manager.user_id and manager.user_id.partner_id:
                message = Markup(f"""
                    <b>Alert: The task {task.name}</b> has passed its deadline {task.deadline}.<br/>
                    Please follow up with employee <b>{task.employee_id.name}</b>.
                """)
                task.message_post(
                    body = message,
                    partner_ids = manager.user_id.partner_id.id
                )

    def monthly_scheduled_job(self):
        first_day = fields.Date.today().replace(day=1)
        employees = self.search([])
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
                body = message,
                subtype_xmlid = "mail.mt_comment"
            )