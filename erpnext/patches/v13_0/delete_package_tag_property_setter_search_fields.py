import frappe

def execute():
	frappe.db.sql("""
		DELETE FROM `tabProperty Setter`
		WHERE `tabProperty Setter`.doc_type='Package Tag'
			AND `tabProperty Setter`.property='search_fields'
	""")