frappe.ready(function() {
	// bind events here
	frappe.web_form.set_value('flight_price', 1000);
	// frappe.web_form.set_df_property('flight_price', 'read_only', false);
	// frappe.web_form.set_value('flight', );

	// frappe.web_form.on('flight_price', (field, value) => {
	// 	if (value < 1000) {
	// 		frappe.msgprint('Value must be more than 1000');
	// 		console.log(my_value);
	// 		field.set_value(1001);
	// 	}
	// });
})

