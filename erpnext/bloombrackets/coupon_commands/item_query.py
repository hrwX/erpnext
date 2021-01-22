from frappe.utils import flt
from erpnext.bloombrackets.coupon_commands.utils import flat_item_group_tree_list

CMD_HAS_ITEM = "Has Item"
CMD_HAS_ITEM_MIN_QTY = "Has Item Min Qty"
CMD_ITEM_QTY = "Item Qty"
CMD_ITEM_GROUP_QTY = "Item Group Qty"

def load_commands(commands, for_doctype):

	def has_item(args, ctx):
		item_name = args[0]
		for item in ctx["#VARS"]["doc"].items:
			if item.item_name == item_name:
				return True

		return False

	def has_item_min_qty(args, ctx):
		item_name = args[0]
		min_qty = flt(args[1])
		total_qty = 0
		for item in ctx["#VARS"]["doc"].items:
			if item.item_code == item_name:
				total_qty = total_qty + item.qty

		result = True if total_qty >= min_qty else False
		return result

	def get_item_qty(args, ctx):
		item_name = args[0]
		total_qty = 0
		for item in ctx["#VARS"]["doc"].items:
			if item.item_code == item_name:
				total_qty = total_qty + item.qty
		return total_qty

	def get_item_group_qty(args, ctx):
		item_group_name = args[0]
		total_qty = 0

		# get a list of item group parents we could logically match against
		# Ex: 
		#	In the case of: Accessories -> Cases
		#	If we are looking for accessories and the item is in the cases group
		# 	we would accept that match since cases belong to accessories.
		item_groups = flat_item_group_tree_list(item_group_name)

		for item in ctx["#VARS"]["doc"].items:
			if item.item_group in item_groups:
				total_qty = total_qty + item.qty
		return total_qty

	commands.update({
		CMD_HAS_ITEM: has_item,
		CMD_HAS_ITEM_MIN_QTY: has_item_min_qty,
		CMD_ITEM_QTY: get_item_qty,
		CMD_ITEM_GROUP_QTY: get_item_group_qty
	})

def load_commands_meta(meta, for_doctype):
	meta.update({
		CMD_HAS_ITEM: {
			"description": "Finds item in document.",
			"returns": "boolean",
			"args": [{
				"name": "item_name",
				"description": "The item's name",
				"fieldtype": "Link",
				"options": "Item"
			}]
		},
		
		CMD_HAS_ITEM_MIN_QTY: {
			"description": "Finds item in document with a minimum qty value.",
			"returns": "boolean",
			"args": [{
				"name": "item_name",
				"description": "The item's name",
				"fieldtype": "Link",
				"options": "Item"
			}, {
				"name": "qty",
				"description": "The minimum qty to should match.",
				"fieldtype": "int"
			}]
		},

		CMD_ITEM_QTY: {
			"description": "Returns the qty of a certain item in the document",
			"returns": "int",
			"args": [{
				"name": "item_name",
				"description": "The item's name",
				"fieldtype": "Link",
				"options": "Item"
			}]
		},
		CMD_ITEM_GROUP_QTY: {
			"description": "Returns the qty of a certain item group items in the document",
			"returns": "int",
			"args": [{
				"name": "item_group",
				"description": "The item's group name",
				"fieldtype": "Link",
				"options": "Item Group"
			}]
		},
	})

