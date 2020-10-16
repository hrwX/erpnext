# Copyright (c) 2018, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():

	for cf in ["Delivery Note-column_break_17", "Delivery Note-map_html", "Delivery Note-odometer", "Delivery Note-sb_map"]:
		if frappe.db.exists("Custom Field", cf):
			frappe.delete_doc_if_exists("Custom Field", cf)