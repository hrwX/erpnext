import frappe


def execute():
    delivery_notes = frappe.db.get_all(
        "Delivery Note", {"status": "Out for Delivery"}, "name")
    frappe.reload_doc("stock", "doctype", "delivery_note", force=True)
    
    for delivery_note in delivery_notes:
        frappe.db.set_value("Delivery Note", delivery_note.name, "status", "In Transit")
