from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval_state = fields.Selection(
        [
            ("draft", "Ноорог"),
            ("approved", "Зөвшөөрсөн"), 
            ("reviewed", "Хянасан"),
            ("purchased", "Худалдан авалт"),
        ],
        string="Зөвшөөрлийн төлөв",
        default="draft",
        tracking=True,
    )

    # Transition mapping
    state_transitions = {
        "draft": {"next": "approved", "group": "purchase_approval.group_manager"},
        "approved": {"next": "reviewed", "group": "purchase_approval.group_controller"},
        "reviewed": {"next": "purchased", "group": "purchase_approval.group_admin"},
    }

    def write(self, values):
        """Override write to enforce stage transitions based on user roles."""
        if "approval_state" in values:
            new_state = values["approval_state"]
            current_state = self.approval_state

            if current_state in self.state_transitions:
                transition = self.state_transitions[current_state]
                if new_state != transition["next"]:
                    raise UserError(
                        f"Invalid transition from {current_state} to {new_state}."
                    )
                if not self.env.user.has_group(transition["group"]):
                    raise UserError(
                        "Та энэ төлөвт шилжих эрхгүй байна. Хандалтын зөвшөөрөл дутуу."
                    )
                # Call the corresponding action method
                self._process_state_action(new_state)

        return super(PurchaseOrder, self).write(values)

    def _process_state_action(self, state):
        """Process the corresponding action based on the state."""
        actions = {
            "approved": self.action_approve,
            "reviewed": self.action_review,
            "purchased": self.action_purchase,
        }
        action = actions.get(state)
        if action:
            action()
        else:
            _logger.warning(f"No action defined for state: {state}")

    def action_approve(self):
        """Approve action for managers."""
        _logger.info(f"Approve action triggered for {self.name}")
        self._send_state_email("approved")

    def action_review(self):
        """Review action for controllers."""
        _logger.info(f"Review action triggered for {self.name}")
        self._send_state_email("reviewed")

    def action_purchase(self):
        """Purchase action for admins."""
        _logger.info(f"Purchase action triggered for {self.name}")
        self._send_state_email("purchased")

    def _send_state_email(self, state):
        """Send an email notification based on the current state."""
        email_templates = {
            "approved": "purchase_approval.email_template_approved",
            "reviewed": "purchase_approval.email_template_reviewed",
            "purchased": "purchase_approval.email_template_purchased",
        }

        template_id = self.env.ref(email_templates.get(state), raise_if_not_found=False)
        if template_id:
            for record in self:
                template_id.send_mail(record.id, force_send=True)
                _logger.info(f"Email sent for state '{state}' on record {record.name}")
        else:
            _logger.warning(f"Email template for state '{state}' not found!")
