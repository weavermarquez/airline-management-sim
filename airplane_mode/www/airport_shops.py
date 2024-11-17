import frappe
from airplane_mode.airport_leasing.doctype.shop.shop import Shop
from frappe.model.docstatus import DocStatus

def get_context(context) -> dict:
    context.shops = shops()
    context.airport = airport
    context.get_desk_link = get_desk_link
    return context

def shops():
    """Call this function to grab a list of all Shops and their associated rooms."""
    shops: list[dict] = _all_shops()
    for shop in shops:
        shop['rooms'] = leased_rooms(shop)
    return shops

def _all_shops() -> list[dict]:
    fields = [
        'name',
        'shop_type',
    ]
    return frappe.get_all('Shop', fields=fields)

def leased_rooms(shop: dict) -> list[str]:
    fields = ['leasing_of']
    filters = {
        'leased_to': shop['name'],
        'docstatus': 1
    }
    return frappe.get_list('Lease', pluck='leasing_of', filters=filters)


def airport(room: str) -> str:
    return frappe.get_cached_value('Room', room, 'airport')


def get_desk_link(shop: dict, doctype: str = 'Shop'):
    name = shop['name']
    html = f'<a href="/app/Form/{doctype}/{name}" style="font-weight: bold;">Shop {name}</a>'
    return html