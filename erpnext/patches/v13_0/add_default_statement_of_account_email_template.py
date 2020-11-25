from __future__ import unicode_literals
import os

import frappe

def execute():
	frappe.reload_doc("email", "doctype", "email_template")
	frappe.reload_doc("accounts", "doctype", "accounts_settings")

	if not frappe.db.exists("Email Template", "Statement of Account"):
		base_path = frappe.get_app_path("erpnext", "templates", "emails")
		response = frappe.read_file(os.path.join(base_path, "statement_of_account_email_notification.html"))

		frappe.get_doc({
			"doctype": "Email Template",
			"name": "Statement of Account",
			"response": response,
			"subject": "Statement of Account",
			"owner": frappe.session.user,
		}).insert(ignore_permissions=True)

	accounts_settings = frappe.get_doc("Accounts Settings")
	accounts_settings.statement_of_account_email_template = "Statement of Account"
	accounts_settings.save()
