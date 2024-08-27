import frappe
no_cache = 1

def get_context(context):
    context.title = "OwO Flight Agency"
    pass
    # context.color = frappe.form_dict.color if frappe.form_dict.color else 'black'
    #Parameter name in /page?name="test" == frappe.form_dict.name