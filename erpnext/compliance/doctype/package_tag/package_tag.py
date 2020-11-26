# -*- coding: utf-8 -*-
# Copyright (c) 2020, Bloom Stack, Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PackageTag(Document):
	def validate(self):
		if self.source_package_tag:
			self.validate_source_package_tag()
			self.update_coa_batch_no()

	def validate_source_package_tag(self):
		source_package_tag = frappe.db.get_value("Package Tag", self.source_package_tag, "source_package_tag")
		if self.name == source_package_tag:
			frappe.throw(_("Invalid package tag. {0} is already the source package for {1}.".format(self.name, self.source_package_tag)))

	def update_coa_batch_no(self):
		self.coa_batch_no = frappe.db.get_value("Package Tag", self.source_package_tag, "coa_batch_no")


@frappe.whitelist()
def get_package_tag_qty(package_tag=None):
	out = 0

	if package_tag:
		out = frappe.db.sql('''select warehouse, sum(actual_qty) as qty
			from `tabStock Ledger Entry`
			where package_tag=%s
			group by warehouse''', package_tag, as_dict=1)

	return out

@frappe.whitelist()
def make_stock_reconciliation(item_code, batch_no, package_tag, qty, warehouse, adjustment_reason):
	stock_reco = frappe.new_doc("Stock Reconciliation")
	stock_reco.purpose = "Stock Reconciliation"
	stock_reco.append("items", {
			"item_code": item_code,
			"qty": qty,
			"warehouse": warehouse,
			"package_tag": package_tag,
			"batch_no": batch_no,
			"adjustment_reason": adjustment_reason
		})
	stock_reco.submit()
	frappe.db.commit()
	return stock_reco