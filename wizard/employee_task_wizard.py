from odoo import api, fields, models

class EmployeeTaskWizard(models.TransientModel):
    _name = 'employee.task.wizard'
    _description = 'Employee Task Wizard'

    employee_id = fields.Many2one('hr.employee', readonly=True)
    task_count = fields.Integer(readonly=True)
    late_task_count = fields.Integer(readonly=True)
    request_count = fields.Integer(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee = self.env['hr.employee'].browse(self.env.context.get('active_id'))
        res.update({
            'employee_id': employee.id,
            'task_count': employee.task_count,
            'late_task_count': employee.late_task_count,
            'request_count': employee.request_count
        })
        return res