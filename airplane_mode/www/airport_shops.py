import frappe
from airplane_mode.airport_leasing.doctype.shop.shop import Shop

def get_context(context) -> dict:
    context.shops = shops()
    context.airport = airport
    context.get_desk_link = get_desk_link
    return context

def shops() -> list[dict]:
    shops: list[dict] = _all_shops()
    for shop in shops:
        shop['rooms'] = Shop.rooms(shop)
    return shops

def _all_shops() -> list[dict]:
    fields = [
        'name',
        'shop_type',
    ]
    return frappe.get_all('Shop', fields=fields)

def get_desk_link(shop: (dict | Shop), *, doctype='Shop') -> str:
    name = shop.get('name')
    html = f'<a href="/app/Form/{doctype}/{name}" style="font-weight: bold;">Shop {name}</a>'
    return html

def airport(room_name: str) -> str:
    return frappe.get_cached_value('Room', room_name, 'airport')