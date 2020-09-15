# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Driver(Document):

	def validate(self):
		if not self.user_id:
			return

		self.employee = frappe.db.get_value("Employee", {"user_id": self.user_id}) or None
