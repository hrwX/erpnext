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
	calculate_total_harvest_weight: (frm) => {
		let total_weight = 0;
		if (frm.doc.plants) {
			frm.doc.plants.forEach(plant => {
				total_weight += plant.harvest_weight;
			});
		}
		frm.set_value("total_harvest_weight", total_weight);
	},
});
frappe.ui.form.on('Harvest Plant', {
	harvest_weight: function (frm) {
		frm.trigger("calculate_total_harvest_weight");
	},

	plants_remove: function (frm) {
		frm.trigger("calculate_total_harvest_weight");
	}
});
