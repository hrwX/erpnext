import frappe
from frappe.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes

def execute():
   doc = frappe.get_doc('Global Search Settings')
   doc.delete()
   update_global_search_doctypes()