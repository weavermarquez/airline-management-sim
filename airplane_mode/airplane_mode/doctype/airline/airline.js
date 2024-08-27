// Copyright (c) 2024, Weaver Marquez and contributors
// For license information, please see license.txt

frappe.ui.form.on("Airline", {
	refresh(frm) {
        if (frm.doc.website != null) {
            frm.add_web_link(frm.doc.website, "Visit Website");
        }
	},
});