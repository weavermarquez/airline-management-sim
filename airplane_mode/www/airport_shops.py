import frappe
from airplane_mode.airport_leasing.doctype.shop.shop import Shop
no_cache = 1

def get_context(context) -> dict:
    context.title = "OwO Airport Storefronts"
    context.show_sidebar = True
    context.airport_leasing_settings = frappe.get_doc('Airport Leasing Settings')
    context.shops = retrieve_shops()
    return context

def retrieve_shops() -> list[Shop]:
    return frappe.get_list('Shop', fields='*')


    # context.color = frappe.form_dict.color if frappe.form_dict.color else 'black'
    #Parameter name in /page?name="test" == frappe.form_dict.name