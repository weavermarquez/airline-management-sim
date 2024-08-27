# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Airline(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		customer_care_number: DF.Data
		founding_year: DF.Int
		headquarters: DF.Data
		website: DF.Data | None
	# end: auto-generated types
	pass
