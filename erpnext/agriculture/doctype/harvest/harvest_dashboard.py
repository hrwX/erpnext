from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'harvest',
		'transactions': [
			{
				'label': _('Referencce'),
				'items': ['Stock Entry']
			}
		]
	}
