# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from erpnext import get_company_currency, get_default_company
from frappe.utils import getdate, flt, date_diff
from frappe import _, _dict
from six import iteritems
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from collections import OrderedDict
from erpnext.accounts.report.general_ledger.general_ledger import validate_party, set_account_currency

def execute(filters=None):
	if not filters:
		return [], []

	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	if filters.get('party'):
		filters.party = frappe.parse_json(filters.get("party"))

	validate_filters(filters, account_details)

	if filters.get('party_type'):
		validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res


def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_customer(filters, gl_entries)

	result = data

	return result

def get_gl_entries(filters):
	select_fields = """, GLE.debit, GLE.credit, GLE.debit_in_account_currency,
		GLE.credit_in_account_currency """

	order_by_statement = "order by GLE.party, GLE.posting_date, GLE.creation"

	gl_entries = frappe.db.sql(
		"""
		SELECT
			GLE.name as gl_entry, GLE.posting_date, GLE.account, GLE.party_type, GLE.party, GLE.voucher_type,
			GLE.voucher_no, GLE.cost_center, GLE.project, GLE.against_voucher_type, GLE.against_voucher,
			GLE.account_currency, GLE.remarks, GLE.against, GLE.is_opening, PE.reference_date,
			SI.posting_date as against_voucher_date {select_fields}
		FROM
			`tabGL Entry` GLE
		INNER JOIN
			`tabSales Invoice` SI
		ON
			GLE.against_voucher=SI.name
		INNER JOIN
			`tabPayment Entry` PE
		ON
			GLE.voucher_no=PE.name
		Where
			GLE.company=%(company)s AND (GLE.party IS NOT NULL)
			{conditions}
			{order_by_statement}
		""".format(select_fields=select_fields,
				conditions=get_conditions(filters),
				order_by_statement=order_by_statement), filters, as_dict=1)

	return gl_entries


def get_conditions(filters):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""GLE.account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))


	if filters.get("party_type"):
		conditions.append("GLE.party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("GLE.party in %(party)s")

	if not (filters.get("account") or filters.get("party")):
		conditions.append("GLE.posting_date >=%(from_date)s")

	conditions.append("(GLE.posting_date <=%(to_date)s and GLE.voucher_type != GLE.against_voucher_type) and GLE.posting_date != SI.posting_date")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("GL Entry")

	if match_conditions:
		conditions.append(match_conditions)

	accounting_dimensions = get_accounting_dimensions(as_list=False)

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value('DocType', dimension.document_type, 'is_tree'):
					filters[dimension.fieldname] = get_dimension_with_children(dimension.document_type,
						filters.get(dimension.fieldname))
					conditions.append("{0} in %({0})s".format(dimension.fieldname))
				else:
					conditions.append("{0} in (%({0})s)".format(dimension.fieldname))

	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_data_with_customer(filters, gl_entries):
	data = []

	gle_map = initialize_gle_map(gl_entries, filters)

	totals, entries = get_customerwise_gle(filters, gl_entries, gle_map)

	for acc, acc_dict in iteritems(gle_map):
		# acc
		if acc_dict.entries:
			# opening shows the customer name
			data.append(acc_dict.totals.opening)

			if not filters.get("accumulated_average_days_to_pay"):
				# entries section shows the gl entry information
				data += acc_dict.entries

				# Total Average Days to Pay section
				data.append(acc_dict.totals.total)
				data.append({})

	return data

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()
	group_by = 'party'

	for gle in gl_entries:
		gle_map.setdefault(gle.get(group_by), _dict(totals=get_totals_dict(gle.party), entries=[]))
	
	return gle_map

def get_totals_dict(party=None):
	def _get_debit_credit_dict(label):
		return _dict(
			account="'{0}'".format(label),
			average_days_to_pay=0.0,
			total = 0.0,
			count = 0.0
		)
	return _dict(
		opening = _get_debit_credit_dict(party),
		total = _get_debit_credit_dict(_('Total Average Days to Pay')),
		closing = _get_debit_credit_dict(_('Closing'))
	)


def get_customerwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []
	group_by = 'party'
	def update_value_in_dict(data, key, gle):
		data[key].total += flt(date_diff(gle.get('reference_date') or gle.get('posting_date'), gle.get("against_voucher_date")))
		data[key].count += 1
		data[key].average_days_to_pay = flt(data[key].total/data[key].count)

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if (gle.posting_date < from_date):
			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'opening', gle)

			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'closing', gle)

		elif gle.posting_date <= to_date:
			if filters.get("accumulated_average_days_to_pay"):
				update_value_in_dict(gle_map[gle.get(group_by)].totals, 'opening', gle)
			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'total', gle)

			average_days_to_pay = date_diff(gle.get('reference_date') or gle.get('posting_date'), gle.get("against_voucher_date"))
			gle['average_days_to_pay'] = average_days_to_pay
			gle_map[gle.get(group_by)].entries.append(gle)

	return totals, entries

def get_columns(filters):
	columns = [
		{
			"label": _("Description"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 160
		}]
	if not filters.get("accumulated_average_days_to_pay"):
		columns += [
			{
				"label": _("Invoice Date"),
				"fieldname": "against_voucher_date",
				"fieldtype": "Date",
				"width": 100
			},
			{
				"label": _("Invoice"),
				"fieldname": "against_voucher_type",
				"width": 100
			},
			{
				"label": _("Invoice Number"),
				"fieldname": "against_voucher",
				"fieldtype": "Dynamic Link",
				"options": "against_voucher_type",
				"width": 140
			},
			{
				"label": _("Payment"),
				"fieldname": "voucher_type",
				"width": 100
			},
			{
				"label": _("Payment Reference"),
				"fieldname": "voucher_no",
				"fieldtype": "Dynamic Link",
				"options": "voucher_type",
				"width": 150
			},
			{
				"label": _("Posting Date"),
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"width": 100
			},
			{
				"label": _("Payment Date"),
				"fieldname": "reference_date",
				"fieldtype": "Date",
				"width": 100
			}
		]
	columns += [
		{
			"label": _("Avarge Days to Pay"),
			"fieldname": "average_days_to_pay",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150
		}
	]
	return columns