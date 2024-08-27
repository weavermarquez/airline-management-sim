// Copyright (c) 2024, Weaver Marquez and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Airplane Add-on Cart", {
// 	refresh(frm) {

// 	},
// });


// frappe.ui.form.on("Airplane Add-on Cart", "onload", function(frm) {
//     frm.set_query("option", "cart_items", function() {
//         return {
//             "filters": {
//                 "account_type": "Bank",
//                 "group_or_ledger": "Ledger"
//             }
//         };
//     });
// });

frappe.ui.form.on('Airplane Add-on Cart', {
    // cdt is Child DocType name i.e Quotation Item
    // cdn is the row name for e.g bbfcb8da6a
    item_code(frm, cdt, cdn) {
        console.log(frappe.get_doc(cdt, cdn));
    }
});
