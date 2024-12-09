from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('reviewed', 'Reviewed'),
        ('purchased', 'Purchased')
    ], string='Approval State', default='draft', tracking=True)

    def action_approve(self):
        self.ensure_one()
        self.write({'approval_state': 'approved'})
        self.send_approval_email('approved')

    def action_review(self):
        self.ensure_one()
        self.write({'approval_state': 'reviewed'})
        self.send_approval_email('reviewed')

    def action_purchase(self):
        self.ensure_one()
        self.write({'approval_state': 'purchased'})
        self.send_approval_email('purchased')

    def purchase_approval(self):
        self.ensure_one()
        if self.approval_state == 'draft':
            self.action_approve()
        elif self.approval_state == 'approved':
            self.action_review()
        elif self.approval_state == 'reviewed':
            self.action_purchase()
        else:
            raise UserError('The purchase order has already been completed.')

    def send_approval_email(self, state):
        template = self.env.ref(f'custom_purchase_approval.email_template_{state}')
        if template:
            template.send_mail(self.id, force_send=True)