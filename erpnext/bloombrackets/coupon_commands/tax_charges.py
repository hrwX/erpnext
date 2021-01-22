from frappe import _dict
from frappe.utils import flt
import json

CMD_DEDUCT_CHARGE = "Apply Charges Discount"
CMD_DEDUCT_SHIPPING = "Deduct Shipping Charge"
CMD_DEDUCT_SHIPPING_PERCENT = "Deduct Shipping Charge Percent"

def apply_tax_charge(doc, coupon, account_head, add_deduct_tax, charge_type, tax_amount, description):
	found = False
	charge = {}
	for item in doc.taxes:
		if item.description == description:
			charge = item
			found = True
			break

	charge.update({
		"category": "Total",
		"account_head": account_head,
		"add_deduct_tax": add_deduct_tax,
		"charge_type": charge_type,
		"tax_amount": flt(tax_amount),
		"description": description,
		"automation_data": json.dumps({
			"linked_coupon": coupon.name
		})
	})

	if not found:
		print(charge)
		doc.append("taxes", charge)


def load_commands(commands, for_doctype):

	def deduct_charge(args, ctx):
		doc = ctx["#VARS"]["doc"]
		coupon = ctx["#VARS"]["coupon"]

		apply_tax_charge(
			doc,
			coupon,
			args[1],
			"Deduct",
			"Actual",
			flt(args[2]),
			args[3]
		)
	
	def deduct_shipping(args, ctx):
		doc = ctx["#VARS"]["doc"]
		coupon = ctx["#VARS"]["coupon"]

		shipping_charge = None
		# find previous shipping charge charge
		for charge in doc.taxes:
			if "shipping" in (charge.description or "").lower():
				shipping_charge = charge
				break

		if not shipping_charge:
			return

		tax_amount = flt(args[1])
		if tax_amount > shipping_charge.tax_amount:
			tax_amount = shipping_charge.tax_amount

		apply_tax_charge(
			doc,
			coupon,
			args[0],
			"Deduct",
			"Actual",
			flt(args[1]),
			"Shipping Discount"
		)

	def deduct_shipping_percent(args, ctx):
		doc = ctx["#VARS"]["doc"]
		coupon = ctx["#VARS"]["coupon"]
		percent = flt(args[1])

		if percent < 0:
			percent = 0
		if percent > 100:
			percent = 100

		shipping_charge = None
		# find previous shipping charge charge
		for charge in doc.taxes:
			if "shipping" in (charge.description or "").lower():
				shipping_charge = charge
				break

		if not shipping_charge:
			return

		tax_amount = (shipping_charge.tax_amount * percent) / 100
		if tax_amount > shipping_charge.tax_amount:
			tax_amount = shipping_charge.tax_amount
		
		if tax_amount < 0:
			tax_amount = 0

		apply_tax_charge(
			doc=doc,
			coupon=coupon,
			account_head=args[0],
			add_deduct_tax="Deduct",
			charge_type="Actual",
			tax_amount=tax_amount,
			description="Shipping Discount"
		)

	commands.update({
		CMD_DEDUCT_CHARGE: deduct_charge,
		CMD_DEDUCT_SHIPPING: deduct_shipping,
		CMD_DEDUCT_SHIPPING_PERCENT: deduct_shipping_percent,
	})

def load_commands_meta(meta, for_doctype):
	meta.update({
		CMD_DEDUCT_CHARGE: {
			"description": "Adds a deduction charge on the document.",
			"args": [{
				"name": "account_head",
				"description": "The account head this charge belongs to",
				"fieldtype": "Link",
				"options": "Account"
			}, {
				"name": "amount",
				"description": "The amount to deduct",
				"fieldtype": "Currency"
			}, {
				"name": "label",
				"description": "The charge label as displayed on reports. Also used to match existing charges.",
				"fieldtype": "string"
			}]
		},
		
		CMD_DEDUCT_SHIPPING: {
			"description": "Adds a deduction shipping charge to the document.",
			"args": [{
				"name": "account_head",
				"description": "The account head this charge belongs to",
				"fieldtype": "Link",
				"options": "Account"
			}, {
				"name": "amount",
				"description": "The amount to deduct",
				"fieldtype": "Currency"
			}]
		},

		CMD_DEDUCT_SHIPPING_PERCENT: {
			"description": "Adds a percent deduction shipping charge to the document based on any existing charge that includes the words 'Shipping' on its description.",
			"args": [{
				"name": "account_head",
				"description": "The account head this charge belongs to",
				"fieldtype": "Link",
				"options": "Account"
			}, {
				"name": "percent",
				"description": "The percent discount. This is calculated from an existing shipping charge.",
				"fieldtype": "Currency"
			}]
		},
	})

