// Copyright (c) 2024, Weaver Marquez and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airplane Ticket", {
	refresh(frm) {
        // Custom buttons
        frm.add_custom_button(_('Assign Seat'), () => {
            frappe.prompt(_('Seat Number'), ({ value }) => frm.set_value('seat', value), _('Select Seat'), _('Assign'));
        }, 'Actions');
	},
});

// add a custom button like the one shown above in Airplane Ticket form view 
// on click, show a dialog with an input field to get the seat number and set it to Seat