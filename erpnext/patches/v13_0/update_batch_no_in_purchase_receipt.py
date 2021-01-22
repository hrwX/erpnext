import frappe

def execute():
    frappe.reload_doc("stock", "doctype", "purchase_receipt")
    docs = frappe.get_all("Purchase Receipt")
    for doc in docs:
        batch_no = frappe.db.get_value("Purchase Receipt Item", {'parent': doc.name}, "batch_no")
        frappe.db.set_value("Purchase Receipt", doc, "batch_no", batch_no, update_modified=False)
