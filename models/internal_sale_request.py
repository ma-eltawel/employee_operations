from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InternalSalesRequest(models.Model):
    _name = 'internal.sale.request'
    _description = 'Internal Sales Request Management'

    name = fields.Char(readonly=1, default='New')
    employee_id = fields.Many2one('hr.employee')
    amount = fields.Float()
    reason = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    approval_level = fields.Selection([
        ('manager', 'Manager'),
        ('department_manager', 'Department Manager'),
        ('finance_manager', 'Finance Manager')
    ],compute='_compute_approval_level')
    approved_by_id = fields.Many2one('res.users')
    approval_date = fields.Datetime()
    approval_month = fields.Char(compute='_compute_approval_month', store=1)
    manager_comment = fields.Text()

    @api.depends('amount')
    def _compute_approval_level(self):
        for rec in self:
            if rec.amount <= 5000:
                rec.approval_level = 'manager'
            elif rec.amount < 10000:
                rec.approval_level = 'department_manager'
            else:
                rec.approval_level = 'finance_manager'

    def action_submitted(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approved(self):
        for rec in self:
            rec.write({
                'state': 'approved',
                'approved_by_id': self.env.user.id,
                'approval_date': fields.Datetime.now()
            })

    def action_rejected(self):
        for rec in self:
            if not rec.manager_comment:
                raise ValidationError('Manager comment is empty!')
            rec.state = 'rejected'

    @api.model_create_multi
    def create(self, vals):
        res = super(InternalSalesRequest, self).create(vals)
        for rec in res:
            rec.name = rec.env['ir.sequence'].next_by_code('sale_request_seq')
        return res

    @api.depends('approval_date')
    def _compute_approval_month(self):
        for rec in self:
            rec.approval_month = rec.approval_date.strftime('%Y-%m') if rec.approval_date else False