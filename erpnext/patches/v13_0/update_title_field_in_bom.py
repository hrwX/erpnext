import frappe

def execute():
    # Update the title of all BOM.
    frappe.reload_doc('manufacturing', 'doctype', 'bom')
    frappe.db.sql("""UPDATE `tabBOM` set title=item_name""")
