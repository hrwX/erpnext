import frappe
from frappe import _

def get_data(data):
	return frappe._dict({
		'fieldname': 'contract',
		'internal_links': {
			'Project': 'project'
		},
		'transactions': [
			{
				'label': _('Sales'),
				'items': ['Sales Order']
			},
			{
				'label': _('Projects'),
				'items': ['Project']
			}
		]
	})
