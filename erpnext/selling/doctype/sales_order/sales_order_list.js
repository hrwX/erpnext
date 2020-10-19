frappe.listview_settings['Sales Order'] = {
	add_fields: ["base_grand_total", "customer_name", "currency", "delivery_date",
		"per_delivered", "per_billed", "status", "order_type", "name", "skip_delivery_note"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			// Closed
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "On Hold") {
			// on hold
			return [__("On Hold"), "orange", "status,=,On Hold"];
		} else if (doc.status === "Completed") {
			return [__("Completed"), "green", "status,=,Completed"];
		} else if (!doc.skip_delivery_note && flt(doc.per_delivered, 6) < 100) {
			if (frappe.datetime.get_diff(doc.delivery_date) < 0) {
			// not delivered & overdue
				return [__("Overdue"), "red",
					"per_delivered,<,100|delivery_date,<,Today|status,!=,Closed"];
			} else if (flt(doc.grand_total) === 0) {
				// not delivered (zero-amount order)
				return [__("To Deliver"), "orange",
					"per_delivered,<,100|grand_total,=,0|status,!=,Closed"];
			} else if (flt(doc.per_billed, 6) < 100) {
				// not delivered & not billed
				return [__("To Deliver and Bill"), "orange",
					"per_delivered,<,100|per_billed,<,100|status,!=,Closed"];
			} else {
				// not billed
				return [__("To Deliver"), "orange",
					"per_delivered,<,100|per_billed,=,100|status,!=,Closed"];
			}
		} else if ((flt(doc.per_delivered, 6) === 100) && flt(doc.grand_total) !== 0
			&& flt(doc.per_billed, 6) < 100) {
			// to bill
			return [__("To Bill"), "orange",
				"per_delivered,=,100|per_billed,<,100|status,!=,Closed"];
		} else if (doc.skip_delivery_note && flt(doc.per_billed, 6) < 100){
			return [__("To Bill"), "orange", "per_billed,<,100|status,!=,Closed"];
		}
	},
	onload: function(listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";

		listview.page.add_menu_item(__("Close"), function() {
			listview.call_for_selected_items(method, {"status": "Closed"});
		});

		listview.page.add_menu_item(__("Re-open"), function() {
			listview.call_for_selected_items(method, {"status": "Submitted"});
		});

		const send_email_action = () => {
			const selected_docs = listview.get_checked_items();
			const doctype = listview.doctype;

			if(selected_docs.length <= 0) return;

			let title = selected_docs[0].title;

			for (let doc of selected_docs) {
				if (doc.docstatus !== 1) {
					frappe.throw(__("Cannot Email Draft or cancelled documents"));
				}

				if (doc.title !== title) {
					frappe.throw(__("Select only one customer's sales orders"));
				}
			};

			frappe.call({
				method: "erpnext.utilities.utils.get_contact",
				args: {
					doctype: doctype,
					name: selected_docs[0].name,
					contact_field: "customer"
				},
				callback: function (r) {
					frappe.call({
						method: "erpnext.utilities.utils.get_document_links",
						args: {
							doctype: doctype,
							docs: selected_docs
						},
						callback: function (res) {
							new frappe.views.CommunicationComposer({
								subject: `${frappe.sys_defaults.company} - ${doctype} links`,
								recipients: r.message ? r.message.email_id : null,
								message: res.message,
								doc: {}
							});
						}
					});
				}
			});
		};

		listview.page.add_actions_menu_item(__('Create Pick Lists'), get_action(listview, "Pick List",
			"erpnext.selling.doctype.sales_order.sales_order.create_multiple_pick_lists"), false);
		listview.page.add_actions_menu_item(__('Create Sales Invoices'), get_action(listview, "Sales Invoice",
			"erpnext.selling.doctype.sales_order.sales_order.create_multiple_sales_invoices"), false);
		listview.page.add_actions_menu_item(__('Create Delivery Note'), get_action(listview, "Delivery Note",
			"erpnext.selling.doctype.sales_order.sales_order.create_muliple_delivery_notes"), false);
		listview.page.add_actions_menu_item(__('Email'), send_email_action, true);
	}
};

function get_action(listview, dt, method) {
	return () => {
		const selected_docs = listview.get_checked_items();
		const docnames = listview.get_checked_items(true);

		if (selected_docs.length <= 0) return;

		for (let doc of selected_docs) {
			if (doc.docstatus !== 1 || ["On Hold", "Closed"].includes(doc.status)) {
				frappe.throw(__("Cannot create a {0} from {1} orders.", [dt, doc.status.bold()]));
			}
		};

		frappe.confirm(__(`This will create a {0} for each Sales Order.<br><br>
			Are you sure you want to create {1} {2}(s) ?`, [dt, selected_docs.length, dt]),
			() => {
				frappe.call({
					method: method,
					args: {
						orders: docnames
					},
					freeze: true,
					callback: (r) => {
						if (r.exc || r.message.length === 0) return;

						let message = ``;
						let scrubbed_doctype = frappe.scrub(dt)

						// loop through each created order and render linked Documents
						let created_order_message = null;
						let created_orders = r.message.filter(order => order.created === true);

						for (let created_order of created_orders) {
							let order_details = created_order[scrubbed_doctype]
								.map(order => frappe.utils.get_form_link(dt, order, true))
								.join(", ");

							created_order_message += ```<li>
								<strong>${order.customer}</strong> (${order.sales_order}): ${order_details}
							</li>```;
						}

						if (created_order_message) {
							message += ```The following ${dt} were created:<br><br><ul>${created_order_message}</ul>```;
						}

						// loop through each existing order and render linked Documents
						let existing_order_message = ``;
						let existing_orders = r.message.filter(order => order.created === false);

						for (let existing_order of existing_orders) {
							let details = existing_order[scrubbed_doctype]
								.map(order => frappe.utils.get_form_link(dt, order, true))
								.join(", ");

							existing_order_message += ```<li>
								<strong>${order.customer}</strong> (${order.sales_order}): ${details || "No available items to pick"}
							</li>```;
						}

						if (existing_order_message) {
							message += ```<br>The following orders either have existing ${dt}:<br><br><ul>${existing_order_message}</ul>```;
						}

						frappe.msgprint(__(message));

						// if validation messages are found, append at the bottom of our message
						if (r._server_messages) {
							let server_messages = JSON.parse(r._server_messages);
							for (let server_message of server_messages) {
								frappe.msgprint(__(JSON.parse(server_message).message));
							}
							// delete server messages to avoid Frappe eating up our msgprint
							delete r._server_messages;
						}

						listview.refresh();
					}
				});
			});
	}
}