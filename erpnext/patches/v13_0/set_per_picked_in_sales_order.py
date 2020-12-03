import frappe

def execute():
	"""
	Set Percentage Picked(per_picked)in Sales Order on the basis of Pick List created and status.
	"""
	frappe.reload_doc('selling', 'doctype', 'sales_order', force=True)
	frappe.reload_doc('stock', 'doctype', 'pick_list_item', force=True)
	sales_orders = frappe.get_all("Sales Order",
		filters={"docstatus": 1},
		fields=["name", "per_delivered", "per_billed"])

	for order in sales_orders:
		pick_list_items = frappe.get_all("Pick List Item",
			filters={"docstatus": 1, "sales_order": order.name},
			fields= ["sum(qty) as total_qty", "sum(picked_qty) as picked_qty"],
			group_by="item_code")
		picked_qty = sum(d['picked_qty'] for d in pick_list_items)
		ordered_qty = sum(d['total_qty'] for d in pick_list_items)

		if ordered_qty:
			per_picked = (picked_qty / ordered_qty) * 100
			frappe.db.set_value("Sales Order", order.name, "per_picked", per_picked, update_modified=False)
			if per_picked < 100 and order.per_delivered < 100 and order.per_billed == 100:
				frappe.db.set_value("Sales Order", order.name, "status", "To Pick", update_modified=False)
			elif per_picked < 100 and order.per_delivered < 100 and order.per_billed < 100:
				frappe.db.set_value("Sales Order", order.name, "status", "To Pick and Bill", update_modified=False)
