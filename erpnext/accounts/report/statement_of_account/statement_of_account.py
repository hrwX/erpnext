# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from erpnext import get_company_currency, get_default_company
from frappe.utils import getdate, cstr, flt
from frappe import _, _dict
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from collections import OrderedDict
from erpnext.accounts.report.general_ledger.general_ledger import set_account_currency, get_totals_dict, get_balance
from frappe.contacts.doctype.address.address import get_default_address

def execute(filters=None):
	if not filters:
		return [], []

	account_details = {}

	if filters and filters.get('print_in_account_currency') and \
		not filters.get('account'):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	if filters.get('party_type'):
		validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	return columns, res

def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")

	if party:
		if not party_type:
			frappe.throw(_("To filter based on Party, select Party Type first"))
		else:
			if not frappe.db.exists(party_type, party):
				frappe.throw(_("Invalid {0}: {1}").format(party_type, party))


def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	select_fields = """, debit, credit, debit_in_account_currency,
		credit_in_account_currency """

	order_by_statement = "order by posting_date, account, creation"

	gl_entries = frappe.db.sql(
		"""
		select
			name as gl_entry, posting_date, account, party_type, party,
			voucher_type, voucher_no, cost_center, project,
			against_voucher_type, against_voucher, account_currency,
			remarks, against, is_opening {select_fields}
		from `tabGL Entry`
		where company=%(company)s {conditions}
		{order_by_statement}
		""".format(
			select_fields=select_fields, conditions=get_conditions(filters),
			order_by_statement=order_by_statement
		),
		filters, as_dict=1)


	return gl_entries


def get_conditions(filters):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))


	if filters.get("party_type"):
		conditions.append("party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("party=%(party)s")

	if not (filters.get("account") or filters.get("party")):
		conditions.append("posting_date >=%(from_date)s")

	conditions.append("(posting_date <=%(to_date)s or is_opening = 'Yes')")

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


def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []

	gle_map = initialize_gle_map(gl_entries, filters)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	data += entries

	# totals
	data.append(totals.total)

	return data

def initialize_gle_map(gl_entries, filters):
	gle_map = OrderedDict()
	group_by = 'account'

	for gle in gl_entries:
		gle_map.setdefault(gle.get(group_by), _dict(totals=get_totals_dict(), entries=[]))
	return gle_map


def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()
	group_by = 'account'

	def update_value_in_dict(data, key, gle):
		data[key].debit += flt(gle.debit)
		data[key].credit += flt(gle.credit)

		data[key].debit_in_account_currency += flt(gle.debit_in_account_currency)
		data[key].credit_in_account_currency += flt(gle.credit_in_account_currency)

		if data[key].against_voucher and gle.against_voucher:
			data[key].against_voucher += ', ' + gle.against_voucher

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if (gle.posting_date < from_date or
			(cstr(gle.is_opening) == "Yes" and not filters.get("show_opening_entries"))):
			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'opening', gle)
			update_value_in_dict(totals, 'opening', gle)

			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

		elif gle.posting_date <= to_date:
			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'total', gle)
			update_value_in_dict(totals, 'total', gle)
			key = (gle.get("voucher_type"), gle.get("voucher_no"),
				gle.get("account"), gle.get("cost_center"))
			if key not in consolidated_gle:
				consolidated_gle.setdefault(key, gle)
			else:
				update_value_in_dict(consolidated_gle, key, gle)

			update_value_in_dict(gle_map[gle.get(group_by)].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

	for key, value in consolidated_gle.items():
		entries.append(value)

	return totals, entries

def get_result_as_list(data, filters):
	balance = 0

	for d in data:
		if not d.get('posting_date'):
			balance = 0

		balance = get_balance(d, balance, 'debit', 'credit')
		d['balance'] = balance

	return data

def get_columns(filters):
	if filters.get("presentation_currency"):
		currency = filters["presentation_currency"]
	else:
		if filters.get("company"):
			currency = get_company_currency(filters["company"])
		else:
			company = get_default_company()
			currency = get_company_currency(company)

	columns = [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Description"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180
		},
		{
			"label": _("Document"),
			"fieldname": "voucher_type",
			"width": 120
		},
		{
			"label": _("Document No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180
		},
		{
			"label": _("Debit ({0})".format(currency)),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Credit ({0})".format(currency)),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _(" Account Balance ({0})".format(currency)),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 180
		}
	]
	return columns

@frappe.whitelist()
def get_addresses(company=None, party_type=None, party=None):
	if not (company and party_type and party):
		return {}

	company_address, party_address = {}, {}
	default_company_address = get_default_address("Company", company)
	if default_company_address:
		company_address = frappe.get_doc("Address", default_company_address)

	default_party_address = get_default_address(party_type, party)
	if default_party_address:
		party_address = frappe.get_doc("Address", default_party_address)

	return {
		"company": company_address,
		"party": party_address
	}

@frappe.whitelist()
def notify_party(filters, report, html=None):
	filters = frappe._dict(json.loads(filters))
	report = frappe._dict(json.loads(report))
	attachments = [frappe.attach_print(report.doctype, report.report_name, html=html)]
	party = frappe.db.get_value(filters.party_type, filters.party, "email_id")

	if not party:
		frappe.throw(_("Email id is not mentioned in the {0} master for {1}.").format(filters.party_type, frappe.bold(filters.party)))

	#soa_template = soa template stand for statement of account template
	soa_template = frappe.db.get_single_value("Accounts Settings", "statement_of_account_email_template")

	if soa_template:
		email_template = frappe.get_doc("Email Template", soa_template)
		message = frappe.render_template(email_template.response, {
			"party": filters.party,
			"from_date": filters.from_date,
			"to_date": filters.to_date
		})
		subject = email_template.subject
	else:
		subject = report.report_name,
		message = (_("Statement of Account of {0} {1} for period {2} to {3}").format(filters.party_type, frappe.bold(filters.party), frappe.bold(filters.from_date), frappe.bold(filters.to_date)))

	frappe.sendmail(
		recipients = [party],
		subject = subject,
		message = message,
		attachments = attachments,
		reference_doctype = report.doctype,
		reference_name = report.report_name
	)

	return party