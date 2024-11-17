# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Shop(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        address_line1: DF.Data | None
        address_line2: DF.Data | None
        city: DF.Data | None
        country: DF.Data | None
        customer_primary_address: DF.Link | None
        customer_primary_contact: DF.Link | None
        customer_type: DF.ReadOnly | None
        email_id: DF.ReadOnly | None
        mobile_number: DF.Data | None
        owned_by: DF.Link
        pincode: DF.Data | None
        primary_address: DF.Text | None
        shop_name: DF.Data
        shop_number: DF.Int
        shop_type: DF.Literal["Restaurant", "Retail", "Services"]
        state: DF.Data | None
    # end: auto-generated types
    pass


    @staticmethod
    def rooms(shop: dict | Document) -> list[str]:
        fields = ['leasing_of']
        filters = {
            'leased_to': shop.get('name'),
            'docstatus': 1
        }
        return frappe.get_list('Lease', pluck='leasing_of', filters=filters)

