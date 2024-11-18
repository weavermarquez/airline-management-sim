// Copyright (c) 2024, Weaver Marquez and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lease", {
	onload: function (frm) {
		
		frm.set_df_property('periods', 'cannot_add_rows', true);
		frm.set_df_property('periods', 'cannot_delete_rows', true);

		frm.set_df_property('payments', 'cannot_add_rows', true);
		frm.set_df_property('payments', 'cannot_delete_rows', true);

		let grid = frm.fields_dict["payments"].grid
		let grid_button = grid.add_custom_button(
			__('Submit Payment'), 
			() => { frm.events.create_lease_payment(frm) }
		);

		const LEASE_DRAFT_ROOM_STATUS = (['Available', 'Reserved', 'Occupied', 'Maintenance'])
		const LEASE_SUBMIT_ROOM_STATUS = (['Available', 'Reserved'])

		frm.set_query('leasing_of', () => {
			return {
				filters: [
					['status', 'in', LEASE_SUBMIT_ROOM_STATUS]
				]
			}
		});

		// grid_button.removeClass('btn-secondary')
		// .addClass('btn-primary')
		// .addClass('order-1');

		// NOTE Applies a change to all custom buttons.
		// grid.buttons.find('.btn-custom')
		// .removeClass('btn-default')
		// .add_class('btn-primary');
	},

	create_lease_payment: function(frm) {
		frappe.prompt([
			{
				label: 'Payment in the amount of',
				fieldname: 'amount',
				fieldtype: 'Currency',
				default: "500",
				   non_negative: true,
				   reqd: true,
			},
			{
				label: 'Reference Number',
				fieldname: 'reference_no',
				fieldtype: 'Data',
				reqd: true,
				// default: frm.doc.leasing_of,
			},
			], (values) => {
				frm.call({ 
					doc: frm.doc, 
					method: "receive_payment", 
					args: { 
						amount: values.amount,
						reference_no: values.reference_no,
					}
				})
			},
			__('Pay Lease'), 
			__('Submit Payment')
		)
	},
});