import frappe

@frappe.whitelist()
def get_meta(doctype):
	return frappe.get_meta(doctype).as_dict()