// Copyright (c) 2024, Weaver Marquez and contributors
// For license information, please see license.txt

// airplane_mode.airport_leasing.LeaseController = class LeaseController extends ( 
// 	erpnext.TransactionController 
// ) {

// TODO Instead of prompting for money, simply redirect to New Payment Entry
frappe.ui.form.on("Lease", {
    refresh: function (frm) {
        frm.set_df_property('transactions', 'cannot_add_rows', true);
        frm.set_df_property('transactions', 'cannot_delete_rows', true);

        // let grid_button = frm.fields_dict["transactions"].grid.add_custom_button(
        //     __('Pay Rent'), () => frm.events.create_payment_entry(frm))

        let grid = frm.fields_dict["transactions"].grid
        let grid_button = grid.add_custom_button(
			__('Submit Payment'), () => { frappe.prompt(__('Payment of'), 
				({ value }) => frm.call({ doc: frm.doc, method: "create_append_payment_entry", args: { amount: value }})
				, __('Pay Lease'), __('Submit Payment'));
        });

        grid_button.removeClass('btn-secondary')
            .addClass('btn-primary')
            .addClass('order-1');

        // NOTE Applies a change to all custom buttons.
        // frm.fields_dict["transactions"].grid.grid_buttons.find('.btn-custom')
        //     .removeClass('btn-default').addClass('btn-primary');
    },
	on_submit: function (frm) {
		// Refresh the Grid
	},
});
    // create_payment_entry: function(frm) {
    //     // let selected_child_names = frm.fields_dict.transactions.grid.get_selected();
    //     // let selected_child_docs = frm.fields_dict.transactions.grid.get_selected_children();
	// 	// const dialog = new frappe.ui.Dialog({})



	// 	const dialog = new frappe.ui.Dialog({
	// 		title: __("Invoice Payment"),
	// 		// size: "large",
	// 		fields: [
	// 			{
	// 				fieldname: "amount",
	// 				fieldtype: "Currency",
	// 				label: __("Amount to Pay"),
	// 				reqd: 1,
	// 				in_list_view: 1,
	// 				non_negative: 1,
	// 			},
	// 		],
	// 		primary_action_label: __("Pay Amount"),
	// 		primary_action: () => {
	// 			// amount = dialog.fields_dict.amount

	// 			var data = { amount: dialog.fields_dict.amount };

	// 			if (data.amount == 0){
	// 				frappe.msgprint(__("Please enter a payment amount."));
	// 			}
	// 			else{
	// 				frappe.call({
	// 					doc: frm.doc,
	// 					method: "create_append_payment_entry",
	// 					args: {
	// 						amount: data.amount,
	// 					},
	// 					// freeze: true,
	// 					// freeze_message: __("Registering Payment..."),
	// 					// callback: (r) => {
	// 						// frm.doc.__onload.has_unreserved_stock = false;
	// 						// frm.reload_doc();
	// 					// },
	// 				});
	// 				dialog.hide();
	// 			}
	// 		},
	// 	});

	// 	// frm.doc.transactions.forEach((item) => {
	// 	// 	console.log(item.idx)
	// 		// if (item.reserve_stock) {
	// 		// 	let unreserved_qty =
	// 		// 		(flt(item.stock_qty) -
	// 		// 			(item.stock_reserved_qty
	// 		// 				? flt(item.stock_reserved_qty)
	// 		// 				: flt(item.delivered_qty) * flt(item.conversion_factor))) /
	// 		// 		flt(item.conversion_factor);

	// 		// 	if (unreserved_qty > 0) {
	// 		// 		dialog.fields_dict.items.df.data.push({
	// 		// 			__checked: 1,
	// 		// 			sales_order_item: item.name,
	// 		// 			item_code: item.item_code,
	// 		// 			warehouse: item.warehouse,
	// 		// 			qty_to_reserve: unreserved_qty,
	// 		// 		});
	// 		// 	}
	// 		// }
	// 	// });

	// 	// dialog.fields_dict.invoices.grid.refresh();
	// 	dialog.show();


	// 	////////


    //     // let transactions = frm.fields_dict["transactions"].get_value()
	// 	// console.log("UwU I'm in create_payment_entry")

	// 	// frappe.call({
	// 	// 	doc: frm.doc,
	// 	// 	method: "create_append_payment_entry",
	// 	// 	callback: (r) => {
	// 	// 		frm.reload_doc();
	// 	// 	},
	// 	// });

	// 	// console.log("Successfully fucked shit up")
    // },

    // As a model for what to do for create_payment_entry
	// create_stock_reservation_entries(frm) {
	// 	const dialog = new frappe.ui.Dialog({
	// 		title: __("Stock Reservation"),
	// 		size: "extra-large",
	// 		fields: [
	// 			{
	// 				fieldname: "set_warehouse",
	// 				fieldtype: "Link",
	// 				label: __("Set Warehouse"),
	// 				options: "Warehouse",
	// 				default: frm.doc.set_warehouse,
	// 				get_query: () => {
	// 					return {
	// 						filters: [["Warehouse", "is_group", "!=", 1]],
	// 					};
	// 				},
	// 				onchange: () => {
	// 					if (dialog.get_value("set_warehouse")) {
	// 						dialog.fields_dict.items.df.data.forEach((row) => {
	// 							row.warehouse = dialog.get_value("set_warehouse");
	// 						});
	// 						dialog.fields_dict.items.grid.refresh();
	// 					}
	// 				},
	// 			},
	// 			{ fieldtype: "Column Break" },
	// 			{
	// 				fieldname: "add_item",
	// 				fieldtype: "Link",
	// 				label: __("Add Item"),
	// 				options: "Sales Order Item",
	// 				get_query: () => {
	// 					return {
	// 						query: "erpnext.controllers.queries.get_filtered_child_rows",
	// 						filters: {
	// 							parenttype: frm.doc.doctype,
	// 							parent: frm.doc.name,
	// 							reserve_stock: 1,
	// 						},
	// 					};
	// 				},
	// 				onchange: () => {
	// 					let sales_order_item = dialog.get_value("add_item");

	// 					if (sales_order_item) {
	// 						frm.doc.items.forEach((item) => {
	// 							if (item.name === sales_order_item) {
	// 								let unreserved_qty =
	// 									(flt(item.stock_qty) -
	// 										(item.stock_reserved_qty
	// 											? flt(item.stock_reserved_qty)
	// 											: flt(item.delivered_qty) * flt(item.conversion_factor))) /
	// 									flt(item.conversion_factor);

	// 								if (unreserved_qty > 0) {
	// 									dialog.fields_dict.items.df.data.forEach((row) => {
	// 										if (row.sales_order_item === sales_order_item) {
	// 											unreserved_qty -= row.qty_to_reserve;
	// 										}
	// 									});
	// 								}

	// 								dialog.fields_dict.items.df.data.push({
	// 									sales_order_item: item.name,
	// 									item_code: item.item_code,
	// 									warehouse: dialog.get_value("set_warehouse") || item.warehouse,
	// 									qty_to_reserve: Math.max(unreserved_qty, 0),
	// 								});
	// 								dialog.fields_dict.items.grid.refresh();
	// 								dialog.set_value("add_item", undefined);
	// 							}
	// 						});
	// 					}
	// 				},
	// 			},
	// 			{ fieldtype: "Section Break" },
	// 			{
	// 				fieldname: "items",
	// 				fieldtype: "Table",
	// 				label: __("Items to Reserve"),
	// 				allow_bulk_edit: false,
	// 				cannot_add_rows: true,
	// 				cannot_delete_rows: true,
	// 				data: [],
	// 				fields: [
	// 					{
	// 						fieldname: "sales_order_item",
	// 						fieldtype: "Link",
	// 						label: __("Sales Order Item"),
	// 						options: "Sales Order Item",
	// 						reqd: 1,
	// 						in_list_view: 1,
	// 						get_query: () => {
	// 							return {
	// 								query: "erpnext.controllers.queries.get_filtered_child_rows",
	// 								filters: {
	// 									parenttype: frm.doc.doctype,
	// 									parent: frm.doc.name,
	// 									reserve_stock: 1,
	// 								},
	// 							};
	// 						},
	// 						onchange: (event) => {
	// 							if (event) {
	// 								let name = $(event.currentTarget).closest(".grid-row").attr("data-name");
	// 								let item_row =
	// 									dialog.fields_dict.items.grid.grid_rows_by_docname[name].doc;

	// 								frm.doc.items.forEach((item) => {
	// 									if (item.name === item_row.sales_order_item) {
	// 										item_row.item_code = item.item_code;
	// 									}
	// 								});
	// 								dialog.fields_dict.items.grid.refresh();
	// 							}
	// 						},
	// 					},
	// 					{
	// 						fieldname: "item_code",
	// 						fieldtype: "Link",
	// 						label: __("Item Code"),
	// 						options: "Item",
	// 						reqd: 1,
	// 						read_only: 1,
	// 						in_list_view: 1,
	// 					},
	// 					{
	// 						fieldname: "warehouse",
	// 						fieldtype: "Link",
	// 						label: __("Warehouse"),
	// 						options: "Warehouse",
	// 						reqd: 1,
	// 						in_list_view: 1,
	// 						get_query: () => {
	// 							return {
	// 								filters: [["Warehouse", "is_group", "!=", 1]],
	// 							};
	// 						},
	// 					},
	// 					{
	// 						fieldname: "qty_to_reserve",
	// 						fieldtype: "Float",
	// 						label: __("Qty"),
	// 						reqd: 1,
	// 						in_list_view: 1,
	// 					},
	// 				],
	// 			},
	// 		],
	// 		primary_action_label: __("Reserve Stock"),
	// 		primary_action: () => {
	// 			var data = { items: dialog.fields_dict.items.grid.get_selected_children() };

	// 			if (data.items && data.items.length > 0) {
	// 				frappe.call({
	// 					doc: frm.doc,
	// 					method: "create_stock_reservation_entries",
	// 					args: {
	// 						items_details: data.items,
	// 						notify: true,
	// 					},
	// 					freeze: true,
	// 					freeze_message: __("Reserving Stock..."),
	// 					callback: (r) => {
	// 						frm.doc.__onload.has_unreserved_stock = false;
	// 						frm.reload_doc();
	// 					},
	// 				});

	// 				dialog.hide();
	// 			} else {
	// 				frappe.msgprint(__("Please select items to reserve."));
	// 			}
	// 		},
	// 	});

	// 	frm.doc.items.forEach((item) => {
	// 		if (item.reserve_stock) {
	// 			let unreserved_qty =
	// 				(flt(item.stock_qty) -
	// 					(item.stock_reserved_qty
	// 						? flt(item.stock_reserved_qty)
	// 						: flt(item.delivered_qty) * flt(item.conversion_factor))) /
	// 				flt(item.conversion_factor);

	// 			if (unreserved_qty > 0) {
	// 				dialog.fields_dict.items.df.data.push({
	// 					__checked: 1,
	// 					sales_order_item: item.name,
	// 					item_code: item.item_code,
	// 					warehouse: item.warehouse,
	// 					qty_to_reserve: unreserved_qty,
	// 				});
	// 			}
	// 		}
	// 	});

	// 	dialog.fields_dict.items.grid.refresh();
	// 	dialog.show();
	// },



frappe.ui.form.on("Lease Transaction", {
    pay_rent: function (frm, cdt, cdn) {
        console.log("Ohh, I presssed a Button in a grid?")
    },
});
