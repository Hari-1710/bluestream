# Copyright (c) 2025, Hari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class PQDandSubmittals(Document):

    def before_insert(self):
        """Set Date of Creation on draft creation"""
        if not self.date_of_creation:
            self.date_of_creation = self.creation

    def before_submit(self):
        """Set Date of Submission or Resubmission"""
        if not self.date_of_submission and not self.amended_from:
            self.date_of_submission = nowdate()

        if self.amended_from:
            self.date_of_resubmission = nowdate()

    def on_cancel(self):
        """Set Date of Revision when cancelled"""
        if not self.date_of_revision:
            self.date_of_revision = nowdate()
