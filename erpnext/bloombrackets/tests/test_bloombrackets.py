import frappe
import unittest

from unittest.mock import patch
from frappe import _dict
from frappe.model.document import Document
from frappe.utils.mock import mock_meta, build_get_meta_side_effects, build_get_doc_side_effect
from erpnext.bloombrackets import resolve_expression
from erpnext.bloombrackets.commands import *

QUOTATION_META = mock_meta("Quotation", fields=[
	{ "fieldname": "name", "fieldtype": "Data" },
	{ "fieldname": "customer_name", "fieldtype": "Link", "options": "Customer" }
])

CUSTOMER_META = mock_meta("Customer", fields=[
	{ "fieldname": "name", "fieldtype": "Data" },
	{ "fieldname": "full_name", "fieldtype": "Data" }
])

class TestBloomBrackets(unittest.TestCase):
	def test_reduce_cmd(self):
		array_values = [1, 2, 3, 4]
		value = resolve_expression([CMD_ARRAY, 1, 2, 3, 4], {})

		self.assertTrue(value == array_values, "{} == {}".format(value, array_values))

	def test_arithmetic(self):
		self.assertTrue(resolve_expression([CMD_ADD, 1, 2], {}) == 3, "1 + 2")
		self.assertTrue(resolve_expression([CMD_SUBTRACT, 1, 2], {}) == -1, "1 - 2")
		self.assertTrue(resolve_expression([CMD_MULTIPLY, 1, 2], {}) == 2, "1 * 2")
		self.assertTrue(resolve_expression([CMD_DIVIDE, 1, 2], {}) == .5, "1 / 2")

	def test_conditionals(self):
		self.assertTrue(resolve_expression([CMD_TRUE, 1, 1], {}) == True, "1 == 1")
		self.assertTrue(resolve_expression([CMD_TRUE, 1, 1, 1], {}) == True, "1 == 1 == 1")
		self.assertTrue(resolve_expression([CMD_FALSE, 1, 2], {}) == True, "1 != 2")
		self.assertTrue(resolve_expression([CMD_FALSE, 1, 2, 3], {}) == True, "1 != 2 != 3")
		self.assertTrue(resolve_expression([CMD_EQUALS, 1, 1], {}) == True, "1 == 1")
		self.assertTrue(resolve_expression([CMD_EQUALS, 1, 1, 1], {}) == True, "1 == 1 == 1")
		self.assertTrue(resolve_expression([CMD_NOT_EQUALS, 1, 2], {}) == True, "1 != 2")
		self.assertTrue(resolve_expression([CMD_NOT_EQUALS, 1, 2, 3], {}) == True, "1 != 2 != 3")

	def test_comparison(self):
		self.assertTrue(resolve_expression([CMD_GREATER_THAN, 2, 1], {}) == True, "2 > 1")
		self.assertTrue(resolve_expression([CMD_GREATER_THAN, 1, 2], {}) == False, "1 > 2")
		self.assertTrue(resolve_expression([CMD_GREATER_AND_EQUAL, 2, 1], {}) == True, "2 >= 1")
		self.assertTrue(resolve_expression([CMD_GREATER_AND_EQUAL, 1, 2], {}) == False, "1 >= 2")
		self.assertTrue(resolve_expression([CMD_LESS_THAN, 1, 2], {}) == True, "1 < 2")
		self.assertTrue(resolve_expression([CMD_LESS_THAN, 2, 1], {}) == False, "2 < 1")
		self.assertTrue(resolve_expression([CMD_LESS_AND_EQUAL, 1, 2], {}) == True, "1 <= 2")
		self.assertTrue(resolve_expression([CMD_LESS_AND_EQUAL, 2, 1], {}) == False, "2 <= 1")

	def test_bitwise_and(self):
		self.assertTrue(resolve_expression([CMD_AND, True, True], {}) == True, "True and True")
		self.assertTrue(resolve_expression([CMD_AND, True, False], {}) == False, "True and False")
		self.assertTrue(resolve_expression([CMD_AND, False, True], {}) == False, "False and True")
		self.assertTrue(resolve_expression([CMD_AND, False, False], {}) == False, "False and False")

	def test_bitwise_or(self):
		self.assertTrue(resolve_expression([CMD_OR, True, True], {}) == True, "True or True")
		self.assertTrue(resolve_expression([CMD_OR, True, False], {}) == True, "True or False")
		self.assertTrue(resolve_expression([CMD_OR, False, True], {}) == True, "False or True")
		self.assertTrue(resolve_expression([CMD_OR, False, False], {}) == False, "False or False")

	def test_bitwise_xor(self):
		self.assertTrue(resolve_expression([CMD_XOR, True, True], {}) == False, "True xor True")
		self.assertTrue(resolve_expression([CMD_XOR, True, False], {}) == True, "True xor False")
		self.assertTrue(resolve_expression([CMD_XOR, False, True], {}) == True, "False xor True")
		self.assertTrue(resolve_expression([CMD_XOR, False, False], {}) == False, "False xor False")

	def test_bitwise_not(self):
		self.assertTrue(resolve_expression([CMD_NOT, True, True], {}) == False, "True not True")
		self.assertTrue(resolve_expression([CMD_NOT, True, False], {}) == True, "True not False")
		self.assertTrue(resolve_expression([CMD_NOT, False, True], {}) == True, "False not True")
		self.assertTrue(resolve_expression([CMD_NOT, False, False], {}) == True, "False not False")

	def test_deep_resolve_expression(self):
		complex_bool_array = [CMD_ARRAY, [CMD_EQUALS, 1, 1], [CMD_EQUALS, 1, 2]]
		complex_int_array = [CMD_ARRAY, [CMD_ADD, 1, 1], 3]
		complex_mixed_array = [CMD_ARRAY, [CMD_ADD, 1, [CMD_ADD, 1, 1]], 4, 5]

		self.assertTrue(resolve_expression(complex_bool_array, {}) == [True, False])
		self.assertTrue(resolve_expression(complex_int_array, {}) == [2, 3])
		self.assertTrue(resolve_expression(complex_mixed_array, {}) == [3, 4, 5])

	def test_if_then_else(self):

		script = [CMD_IF, [CMD_NOT_EQUALS, [CMD_VAR, "foo"], "bar"], [
			[CMD_SET, "foo", "bar"]
		], [
			[CMD_SET, "foo", "nvm"],
			[CMD_SET, "foo_set", True]
		]]

		ctx1 = {}
		resolve_expression(script, ctx1)
		self.assertTrue(ctx1.get("#VARS").get("foo") == "bar" and ctx1.get("#VARS").get("foo_set") == None, ctx1.get("#VARS"))

		ctx2 = { "#VARS": { "foo": "bar" } }
		resolve_expression(script, ctx2)
		self.assertTrue(ctx2.get("#VARS").get("foo") == "nvm" and ctx2.get("#VARS").get("foo_set") == True, ctx2.get("#VARS"))

	def test_if_no_else(self):
		script = [CMD_IF, [CMD_NOT_EQUALS, [CMD_VAR, "foo"], "bar"], [
			[CMD_SET, "bar", "foo"]
		]]

		ctx1 = { "#VARS": { "foo": "bar"} }
		resolve_expression(script, ctx1)
		self.assertTrue(ctx1.get("#VARS").get("foo") == "bar" and ctx1.get("#VARS").get("bar") == None, ctx1.get("#VARS"))

	@patch('frappe.new_doc')
	def test_doctype_field_resolve(self, new_doc):
		new_doc.side_effect = [_dict({ "status": "Draft" })]
		ctx = { "#VARS": { "doc": frappe.new_doc("Quotation", {}) } }
		status = resolve_expression([CMD_VAR, "doc", "status"], ctx)

		frappe.new_doc.assert_called_once()
		self.assertTrue(status == "Draft")

	@patch('frappe.get_doc')
	@patch('frappe.get_meta')
	def test_doctype_link_resolve(self, get_meta, get_doc):	
		# set test side effects
		get_meta.side_effect = build_get_meta_side_effects([
			QUOTATION_META, 
			CUSTOMER_META
		])
		get_doc.side_effect= build_get_doc_side_effect([
			Document({
				"doctype": "Quotation",
				"name": "test-quotation",
				"customer_name": "test-customer"
			}),
			Document({
				"doctype": "Customer",
				"name": "test-customer",
				"full_name": "Mr. Test Customer"
			})
		])

		ctx = { "#VARS": { "doc": frappe.get_doc("Quotation", "test-quotation") } }
		full_name = resolve_expression([CMD_VAR, "doc", "customer_name", "full_name"], ctx)

		get_doc.assert_called()
		get_meta.assert_called()
		self.assertTrue(full_name == "Mr. Test Customer")

	