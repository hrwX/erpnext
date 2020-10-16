# Copyright (c) 2020, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():

	for cf in ["Delivery Trip-column_break_17", "Delivery Trip-map_html", "Delivery Trip-odometer", "Delivery Trip-sb_map"]:
		frappe.delete_doc_if_exists("Custom Field", cf)