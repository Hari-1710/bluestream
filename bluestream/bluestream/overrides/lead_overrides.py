# your_app/overrides/custom_lead.py

from erpnext.crm.doctype.lead.lead import Lead

class CustomLead(Lead):
    """
    Override Lead email uniqueness validation.
    Allows duplicate email_id in Lead.
    """

    def check_email_id_is_unique(self):
        # Intentionally override and disable uniqueness check
        return
