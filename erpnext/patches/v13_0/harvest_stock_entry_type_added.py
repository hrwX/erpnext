from __future__ import unicode_literals
import frappe

def execute():
	create_stock_entry_types()

def create_stock_entry_types():
	frappe.reload_doc('stock', 'doctype', 'stock_entry_type')
	frappe.reload_doc('stock', 'doctype', 'stock_entry')

	for purpose in ["Material Issue", "Material Receipt", "Material Transfer",
		"Material Transfer for Manufacture", "Material Consumption for Manufacture", "Manufacture",
		"Repack", "Send to Subcontractor", "Send to Warehouse", "Receive at Warehouse", "Harvest"]:
	   
		ste_type = frappe.get_doc({
			'doctype': 'Stock Entry Type',
			'name': purpose,
			'purpose': "Material Receipt" if purpose == "Harvest" else purpose
		})

		try:
			ste_type.insert()
		except frappe.DuplicateEntryError:
			pass
