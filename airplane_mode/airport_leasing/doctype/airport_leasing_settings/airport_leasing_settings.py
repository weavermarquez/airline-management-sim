# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AirportLeasingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		default_rental_rate: DF.Int
		default_uom: DF.Literal["Week", "Month"]
		enable_payment_reminders: DF.Check
	# end: auto-generated types
	pass
