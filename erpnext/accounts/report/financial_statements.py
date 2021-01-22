# -*- coding: utf-8 -*-

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import re
from past.builtins import cmp
import functools

import frappe, erpnext
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.utils import get_fiscal_year
from frappe import _
from frappe.utils import (flt, getdate, add_months, add_days, formatdate, get_last_day, cstr)

from six import itervalues
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children

def get_period_list(from_custom_date, to_custom_date, periodicity, accumulated_values=False, 
	company=None, reset_period_on_fy_change=True):
	"""
	Returns a list of periods for which data needs to be generated based on periodicity or customized.

	Args:
		from_custom_date (datetype): starting date from which we want to see our financial statements
		to_custom_date (datatype): ending date till which we want to see our financial statements
		periodicity (int): frequency of the fiscal period (monthly, quarterly, yearly, etc)
		accumulated_values (bool, optional): Defaults to False.
		company (string, optional): Name of the company. Defaults to None.
		reset_period_on_fy_change (bool, optional): Defaults to True.

	Returns:
		list of dict: {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
	"""		
	#get start and end dates for the fiscal year(s) in consideration
	from_custom_date = getdate(from_custom_date)
	to_custom_date = getdate(to_custom_date)
	fiscal_year = get_fiscal_year_data(from_custom_date.year, to_custom_date.year)
	validate_fiscal_year(fiscal_year)

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	year_start_date = getdate(fiscal_year.year_start_date)
	year_end_date = getdate(fiscal_year.year_end_date)

	period_list = []
	#select the time duration of our data - fix for first task likely here
	if periodicity!="Custom": 
		period_list = standard_period_lists(periodicity, from_custom_date, to_custom_date, company)
	else: 
		#generate custom period lists
		period = frappe._dict({
			"from_date": getdate(from_custom_date), 
			"to_date": getdate(to_custom_date)
		})
		period.fiscal_year_start_date = get_fiscal_year(period.from_date, company=company)[1]
		period.fiscal_year_end_date = get_fiscal_year(period.to_date, company=company)[0]
		period_list.append(period)

	#adds keys (ex. "feb_2021") and labels () to the period_list data
	for period in period_list:
		#key contains the end period date formatted as "feb_2021"
		key = period["to_date"].strftime("%b_%Y").lower()

		#get the labels used as the column headers in the reports page by calling formatdate
		if not accumulated_values:
			label = get_label(period["from_date"], period["to_date"])
		elif reset_period_on_fy_change:
			label = get_label(period.fiscal_year_start_date, period["to_date"])
		else:
			label = get_label(period_list[0].from_date, period["to_date"])

		period.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list

def standard_period_lists(periodicity, from_custom_date, to_custom_date, company):
	"""
	Generates a list of periods for standard date ranges (monthly, quarterly, yearly)

	Args:
		periodicity (int): the periodicity for which we want our financials (quarterly, year, etc)
		year_start_date (date): irst date of the fiscal period
		year_end_date (date): last date of the fiscal period
		company (string): name of the company

	Returns:
		list of dict: {"from_date": from_date, "to_date": to_date, 
			"fiscal_year_start_date": , "fiscal_year_end_date": }
	"""	
	period_list = []
	months_to_add = {
		"Yearly": 12,
		"Half-Yearly": 6,
		"Quarterly": 3,
		"Monthly": 1
	}[periodicity]

	#start date and no of months between start and end dates
	start_date = from_custom_date
	months = get_months(from_custom_date, to_custom_date)

	#iterate the number of fiscal terms in our data range
	for i in range(months // months_to_add+1):

		#set the start_date, generate the end_date for the period
		period = frappe._dict({
			"from_date": start_date
		})
		to_date = get_period_end_date(start_date, months_to_add)
		#the end date + 1 day of this period will be the start date of the next period
		start_date = add_days(to_date,1)

		if to_date <= to_custom_date:
			# the normal case
			period.to_date = to_date
		else:
			# if a fiscal year ends before a 12 month period
			period.to_date = to_custom_date

		#stores the start and end fiscal year dates in our dictionary
		period.fiscal_year_start_date = get_fiscal_year(period.from_date, company=company)[1]
		period.fiscal_year_end_date = get_fiscal_year(period.to_date, company=company)[0]
		period_list.append(period)

		if period.to_date == to_custom_date:
			break	
	return period_list

#to be merged into frappe later
def get_period_end_date(start_date, months_in_time_frame): 
	"""
	Return the end date for the desired period.

	Args:
		start_date (datetime): starting date of time frame
		months_in_time_frame (int): no of months in the desired period (For example, quarterly = 3)

	Returns:
		datetime: ending date for the requested period
	"""
	current_month = start_date.month
	months_to_add = abs(12-current_month)%months_in_time_frame
	end_date = get_last_day(add_months(start_date, months_to_add))
	return end_date


def get_fiscal_year_data(from_fiscal_year, to_fiscal_year):
	"""
	Returns the start and end dates of the duration we wish to inspect.

	Args:
		from_fiscal_year (int): the starting year of the period we want data for
		to_fiscal_year (int): the ending year of the period we want data till 
		example: (2018, 2019)

	Returns:
		dict: the start and end dates for the period we wish to get data for or {}
			example - {'year_start_date': datetime.date(2018, 1, 1),
  				  'year_end_date': datetime.date(2019, 12, 31)}
	
	"""	
	#get the start and end dates for the duration we want data for
	fiscal_year = frappe.db.sql("""select min(year_start_date) as year_start_date,
		max(year_end_date) as year_end_date from `tabFiscal Year` where
		name between %(from_fiscal_year)s and %(to_fiscal_year)s""",
		{'from_fiscal_year': from_fiscal_year, 'to_fiscal_year': to_fiscal_year}, as_dict=1)

	return fiscal_year[0] if fiscal_year else {}


def validate_fiscal_year(fiscal_year):
	"""
	Checks whether the fiscal year start and end dates are valid, throws error if invalid.

	Args:
		fiscal_year (dict): contains the start and end date of the fiscal year
	"""	
	if not fiscal_year.get('year_start_date') and not fiscal_year.get('year_end_date'):
		frappe.throw(_("End Year cannot be before Start Year"))


def get_months(start_date, end_date):
	"""Returns the number of months between a starting date and and ending date."""
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1


def get_label(from_date, to_date):
	"""
	Returns the title for the column in the financial reports.

	Args:
		from_date (datetime): start date of the period
		to_date (datetime): end date of the period

	Returns:
		string: formatted date based on periodicity
			Ex. for Quarterly, Jan 19-Mar 19
	"""	
	return formatdate(from_date, "MMM dd, YYYY") + " - " + formatdate(to_date, "MMM dd, YYYY")


def get_data(company, root_type, balance_must_be, period_list, filters=None,
				accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
				ignore_accumulated_values_for_fy=False , total = True):
	"""
	Returns the data requested by the concerned financial statement.

	Args:
		company (string): name of the company
		root_type (string): Root of the account (Asset, Liability, Equity, Income, Expense)
		balance_must_be (string): Debit or Credit
		period_list (list of dict): durations/periods for which we want our data 
		filters (list of dict, optional): filters provided by the user on the financial statements page (date range, periodicity, etc). 
			 Defaults to None.
		accumulated_values (int, optional): Defaults to 1.
		only_current_fiscal_year (bool, optional): Defaults to True.
		ignore_closing_entries (bool, optional): Defaults to False.
		ignore_accumulated_values_for_fy (bool, optional): Defaults to False.
		total (bool, optional): Defaults to True.

	Returns:
		list of dicts: contains the data that is rendered to the user
	"""				
	#get the list of accounts associated with a particular root (ex. Asset, Liability, etc)
	accounts = get_accounts(company, root_type)
	if not accounts:
		return None

	#get list and map of parent/child accounts
	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
	company_currency = get_appropriate_currency(company, filters)
	accounts = sort_accounts_by_key(accounts)
	
	#get general ledger entries
	gl_entries_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):

		#Map all ledger entries for an account against the account name
		set_gl_entries_by_account(
			company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt, filters,
			gl_entries_by_account, ignore_closing_entries=ignore_closing_entries
		)

	#calculate the values for the different accounts from GL entries made against them
	calculate_values(accounts_by_name, gl_entries_by_account, period_list, 
						accumulated_values, ignore_accumulated_values_for_fy)
	
	#clean up the data
	out = prepare_data(accounts, balance_must_be, period_list, company_currency)
	
	#create a row for the totals of the root accounts (asset, liability, income, etc)
	if out and total:
		out, parent_accounts_with_nonzero_children = generate_parent_account_totals(out, root_type, 
														balance_must_be, period_list, company_currency)

	#remove rows with zero values and setting parent rows to none
	out = filter_out_zero_value_rows(out, parent_accounts_with_nonzero_children)
	out = nullify_parent_account_values(out, period_list)
	return out

def sort_accounts_by_key(data, key='lft'):
	"""Returns accounts in a list of dicts after sorting them by a given key."""
	return sorted(data, key = lambda i: i[key])


def nullify_parent_account_values(data, period_list): 
	"""
	Setting values of each period for a parent account to zero.

	Args:
		data (list): hashtables of the data prepared for output
		period_list (list): list of periods for which the data needs to be processed

	Returns:
		list: hashtable of the data to be output
	"""	
	for row in data: 
		for period in period_list: 
			if (row.get("is_group",0) or row.get("group_account_summary")) and period.key in row and row[period.key] == 0.0: 
				row[period.key] = None
			
	return data

def get_appropriate_currency(company, filters=None):
	if filters and filters.get("presentation_currency"):
		return filters["presentation_currency"]
	else:
		return frappe.get_cached_value('Company',  company,  "default_currency")


def calculate_values(accounts_by_name, gl_entries_by_account, period_list, 
							accumulated_values, ignore_accumulated_values_for_fy):
	"""
	Calculates the values/accumulated values of the accounts needed in the financial reports.
	
	Modifies the accounts_by_name dictionary by appending the above mentioned calculated values.

	Args:
		accounts_by_name (dict): account details mapped by their name
		gl_entries_by_account (dict): ledger entries mapped to their account names
		period_list (list): duration for which the data is needed
		accumulated_values (int): flag that tells us whether the values need to be accumulated
		ignore_accumulated_values_for_fy (bool): for distinguishing between non accumulating 
			and accumulating accounts
	"""							
	#iterate through all the journal entries account by account
	for entries in itervalues(gl_entries_by_account):
		for entry in entries:
			
			#get the account name for which we are processing ledger entries
			d = accounts_by_name.get(entry.account)
			
			#throw error if account details not retrived
			if not d:
				frappe.throw(_("Could not retrieve information for {0}.".format(entry.account)))
					
			#generate accumulated data for the different periods specified by the user
			for period in period_list:

				# check if posting date is within the period
				if entry.posting_date <= period.to_date:
					
					#we ignore accumulated values for reports like P\L and cash flow
					if (accumulated_values or entry.posting_date >= period.from_date) and \
						(not ignore_accumulated_values_for_fy or
							entry.fiscal_year == period.fiscal_year_end_date):

						#period.key updates the account value for the given period (Week/Month/Year)
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

			if entry.posting_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)


def accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values):
	"""
	Accumulate children's values in parent accounts

	Args:
		accounts (list): parent/child account names arranged by depth
		accounts_by_name (dict): account details mapped by account_name
		period_list (list of dict): time frames across which the data is needed
		accumulated_values (int): whether values are accumulated or not
	"""	
	for d in reversed(accounts):
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = \
					accounts_by_name[d.parent_account].get(period.key, 0.0) + d.get(period.key, 0.0)
			#accumulate the balance in the parent account's opening balance variable
			accounts_by_name[d.parent_account]["opening_balance"] = \
				accounts_by_name[d.parent_account].get("opening_balance", 0.0) + d.get("opening_balance", 0.0)


def prepare_data(accounts, balance_must_be, period_list, company_currency):
	"""
	Creates each row as a dictionary that is finally rendered for the user

	Args:
		accounts (list of dict): parent/child account names arranged by depth
		balance_must_be (string): debit or credit
		period_list (list of dict): list of periods that need to processed
		company_currency (string): currency

	Returns:
		list of dict: each of the rows that need to be rendered 
	"""
	#take the starting and ending date
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")
	
	#loop through all the accounts and create rows for each with neccessary data entries
	for d in accounts:
		has_value = False
		total = 0
		row = frappe._dict({
			"account": _(d.name),
			"parent_account": _(d.parent_account) if d.parent_account else '',
			"lft": d.lft, 
			"rgt": d.rgt,
			"indent": flt(d.indent),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": company_currency,
			"include_in_gross": d.include_in_gross,
			"account_type": d.account_type,
			"is_group": d.is_group,
			"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1),
			"account_name": ('%s - %s' %(_(d.account_number), _(d.account_name))
				if d.account_number else _(d.account_name))
		})
		
		for period in period_list:

			# change sign based on Debit or Credit, since calculation is done using (debit - credit)
			if d.get(period.key) and balance_must_be == "Credit":
				d[period.key] *= -1

			row[period.key] = flt(d.get(period.key, 0.0), 3)

			#ignore zero values
			if abs(row[period.key]) >= 0.005:
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data


def filter_out_zero_value_rows(data, parent_accounts_with_nonzero_children, show_zero_values=False):
	"""
	Remove nongroup accounts with zero values and group accounts with all children with zero values.

	Args:
		data (list of dict): rows of accounts that need to be processed for output
		parent_accounts_with_nonzero_children (set): set of parents that have at least one nonzero child
		show_zero_values (bool, optional): Defaults to False.

	Returns:
		list of dict: rows to be displayed to the user
	"""
	data_with_value = []
	for d in data:
		#adding nonzero group accounts
		if d.get("is_group") and (d.get("account_name") in parent_accounts_with_nonzero_children):
			data_with_value.append(d)

		#adding nonzero group account summaries
		if d.get("group_account_summary") and d.get('has_value'):
			data_with_value.append(d)
			if d.get("indent") == 0:
				data_with_value.append({})

		#adding nonzero nongroup accounts
		if not d.get("group_account_summary") and not d.get("is_group") and d.get("has_value"):
			data_with_value.append(d)

	return data_with_value


def generate_parent_account_totals(out, root_type, balance_must_be, period_list, company_currency):
	"""
	Prepares the total row at the end of the each parent account/root type.

	Args:
		out (list): dictionaries of account details (rows for processing)
		root_type (string): type of account (asset, liability, income, expense, equity)
		balance_must_be (string): default balance type of account (credit/debit)
		period_list (list of dict): periods for which data has to be rendered
		company_currency (string): currency for which data must be generated

	Returns:
		list of dicts: rows of accounts to be displayed, including totals for group accounts
		set: set of parents having children with nonzero values
	"""
	new_output = []
	parent_accounts = []
	parent_accounts_with_nonzero_children = set()
	for row in out:

		#ensure that branch leaves are not marked as parent/group accounts
		if row.get("is_group") and (row.get("rgt") - row.get('lft')) == 1:
			row.update({
				"is_group":0
			})

		#patch for accounts cause lft and rgt branches are inconsistent, will delete once issues is resolved
		if parent_accounts and (parent_accounts[-1].get("rgt") < row.get("rgt")):
			parent_to_append = parent_accounts.pop()

			#create set of parent accounts whose children have nonzero values
			if parent_to_append.get('has_value', None): 
					parent_accounts_with_nonzero_children.add(parent_to_append['account'])
					new_output.append(parent_to_append)

		#add parent accounts to a list
		if row.get("is_group", 0): 
			
			#patch because some Chart of Accounts don't have account numbers
			account_name = row.get("account_name")
			account_summary = account_name.split("-")[1] if "-" in account_name else account_name
			
			#we stack our parent accounts, pop them once all their child accounts have been totaled
			total_parent_account = { 
				"account_name": _("Total {0}").format(_(account_summary)),
				"account": _("{0}").format(_(row.get("account_name"))),
				"lft": _(row.get('lft')),
				"rgt": _(row.get('rgt')),
				"has_value": False,
				"indent": _(row.get('indent')),
				"currency": company_currency,
				"group_account_summary": True
			}
			parent_accounts.append(total_parent_account)

			row['total'] = None
		
		#sum rows if it is not the parent account
		if not row.get("is_group", 0):
			for parent in parent_accounts: 
				
				#if row is child of parent, add value to parent total
				for period in period_list:
					row[period.key] = row.get(period.key, 0.0)
					parent.setdefault(period.key, 0.0)
					parent[period.key] += row.get(period.key, 0.0)
					if parent[period.key]:
						parent['has_value'] = True
					
				#create total values for all the periods
				parent.setdefault("total", 0.0)
				parent["total"] += flt(row["total"])
				row["total"] = None
				#add the parent to a list of parents that have non zero subchildren
				
		#append the row to the final output
		new_output.append(row)
		
	#removing any remaining accounts in the stack, including root account	
	while parent_accounts: 
		parent_to_append = parent_accounts.pop()
		new_output.append(parent_to_append)				
		if parent_to_append.get('has_value'): 
			parent_accounts_with_nonzero_children.add(parent_to_append.get("account"))
		
	return new_output, parent_accounts_with_nonzero_children


def get_accounts(company, root_type):
	"""
	Returns the details of the accounts associated with a particular root_type.

	Args:
		company (string): The name of the company
		root_type (string): the root account, i.e. Assets, Liabilities, etc

	Returns:
		dict: name, account_number, parent_account, lft, rgt, root_type, 
			report_type, account_name, include_in_gross, account_type, is_group, lft, rgt
	"""
	return frappe.db.sql("""
		select name, account_number, parent_account, lft, rgt, root_type, 
		report_type, account_name, include_in_gross, account_type, is_group, lft, rgt
		from `tabAccount`
		where company=%s and root_type=%s order by lft""", (company, root_type), as_dict=True)


def filter_accounts(accounts, depth=10):
	"""
	Returns convenient data structures for processing of accounts.

	Args:
		accounts (list of dict): map of financial account details
		depth (int, optional): Depth of the leaf accounts in the accounts tree. Defaults to 10.

	Returns:
		list: returns a list of parent/child accounts arranged by depth-first-search
			which is used in the final presentation when accounts with their values are listed
		dict: hashmap with key as account name and value as account details
		dict: hashmap of parent account mapped to children accounts
	"""
	parent_children_map = {}
	accounts_by_name = {}

	#maps account name to account details, parent account to child accounts
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	#arranges the accounts in a depth-first-search fashion in filtered_accounts
	filtered_accounts = []
	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent==None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map


def sort_accounts(accounts, is_root=False, key="name"):
	"""Sort root types as Asset, Liability, Equity, Income, Expense."""

	def compare_accounts(a, b):
		if re.split('\W+', a[key])[0].isdigit():
			# if chart of accounts is numbered, then sort by number
			return cmp(a[key], b[key])
		elif is_root:
			if a.report_type != b.report_type and a.report_type == "Balance Sheet":
				return -1
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liability" and b.root_type == "Equity":
				return -1
			if a.root_type == "Income" and b.root_type == "Expense":
				return -1
		else:
			# sort by key (number) or name
			return cmp(a[key], b[key])
		return 1

	accounts.sort(key = functools.cmp_to_key(compare_accounts))

def set_gl_entries_by_account(company, from_date, to_date, root_lft, root_rgt, 
								filters, gl_entries_by_account, ignore_closing_entries=False):
	"""
	Organise the General Ledger by mapping the account name to all of its ledger entries.

	Args:
		company (string): The name of the company
		from_date (datetime): starting date of the time period
		to_date (datetime): ending date of the time period
		root_lft (int): left branch of the the accounts tree
		root_rgt (int): right branch of the accounts tree
		filters (list): list of filters to be applied to the general ledger entries
		gl_entries_by_account (list of dict): GL Entries to be processed
		ignore_closing_entries (bool, optional): Defaults to False.

	Returns:
		dict: {"account": [gl entries], ... }
	"""	
	additional_conditions = get_additional_conditions(from_date, ignore_closing_entries, filters)

	#get a sublist of accounts/child accounts that fall within the tree branch between lft and rgt passed
	accounts = frappe.db.sql_list("""select name from `tabAccount`
		where lft >= %s and rgt <= %s and company = %s order by lft""", (root_lft, root_rgt, company))

	if accounts:
		additional_conditions += " and account in ({})"\
			.format(", ".join([frappe.db.escape(d) for d in accounts]))

		gl_filters = {
			"company": company,
			"from_date": from_date,
			"to_date": to_date,
			"finance_book": cstr(filters.get("finance_book"))
		}

		if filters.get("include_default_book_entries"):
			gl_filters["company_fb"] = frappe.db.get_value("Company",
				company, 'default_finance_book')

		for key, value in filters.items():
			if value:
				gl_filters.update({
					key: value
				})

		gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening, fiscal_year, 
			debit_in_account_currency, credit_in_account_currency, account_currency from `tabGL Entry`
			where company=%(company)s
			{additional_conditions}
			and posting_date <= %(to_date)s
			order by account, posting_date""".format(additional_conditions=additional_conditions), gl_filters, as_dict=True) #nosec

		if filters and filters.get('presentation_currency'):
			convert_to_presentation_currency(gl_entries, get_currency(filters))

		for entry in gl_entries:
			gl_entries_by_account.setdefault(entry.account, []).append(entry)

		return gl_entries_by_account


def get_additional_conditions(from_date, ignore_closing_entries, filters):
	additional_conditions = []

	accounting_dimensions = get_accounting_dimensions(as_list=False)

	if ignore_closing_entries:
		additional_conditions.append("ifnull(voucher_type, '')!='Period Closing Voucher'")

	if from_date:
		additional_conditions.append("posting_date >= %(from_date)s")

	if filters:
		if filters.get("project"):
			if not isinstance(filters.get("project"), list):
				filters.project = frappe.parse_json(filters.get("project"))

			additional_conditions.append("project in %(project)s")

		if filters.get("cost_center"):
			filters.cost_center = get_cost_centers_with_children(filters.cost_center)
			additional_conditions.append("cost_center in %(cost_center)s")

		if filters.get("include_default_book_entries"):
			additional_conditions.append("(finance_book in (%(finance_book)s, %(company_fb)s, '') OR finance_book IS NULL)")
		else:
			additional_conditions.append("(finance_book in (%(finance_book)s, '') OR finance_book IS NULL)")

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value('DocType', dimension.document_type, 'is_tree'):
					filters[dimension.fieldname] = get_dimension_with_children(dimension.document_type,
						filters.get(dimension.fieldname))
					additional_conditions.append("{0} in %({0})s".format(dimension.fieldname))
				else:
					additional_conditions.append("{0} in (%({0})s)".format(dimension.fieldname))

	return " and {}".format(" and ".join(additional_conditions)) if additional_conditions else ""

def get_cost_centers_with_children(cost_centers):
	if not isinstance(cost_centers, list):
		cost_centers = [d.strip() for d in cost_centers.strip().split(',') if d]

	all_cost_centers = []
	for d in cost_centers:
		if frappe.db.exists("Cost Center", d):
			lft, rgt = frappe.db.get_value("Cost Center", d, ["lft", "rgt"])
			children = frappe.get_all("Cost Center", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
			all_cost_centers += [c.name for c in children]
		else:
			frappe.throw(_("Cost Center: {0} does not exist".format(d)))

	return list(set(all_cost_centers))

def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [{
		"fieldname": "account",
		"label": _("Account"),
		"fieldtype": "Link",
		"options": "Account",
		"width": 300
	}]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Currency",
				"width": 150
			})

	return columns
