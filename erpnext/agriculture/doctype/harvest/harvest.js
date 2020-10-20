// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Harvest', {
	setup: function (frm) {
		frm.make_methods = {
			'Stock Entry': () => {
				if (frm.doc.docstatus === 1) {
					frm.trigger("create_stock_entry");
				}
			}
		};
	},
	create_stock_entry: (frm) => {
		frappe.xcall('erpnext.agriculture.doctype.harvest.harvest.create_stock_entry', {
			'harvest': frm.doc.name,
		}).then(stock_entry => {
			frappe.model.sync(stock_entry);
			frappe.set_route("Form", 'Stock Entry', stock_entry.name);
		});
	},
});
