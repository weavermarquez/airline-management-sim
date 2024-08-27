# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Lease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		end_date: DF.Date
		leased_from: DF.Link
		leased_to: DF.Link
		leasing_of: DF.Link
		start_date: DF.Date
	# end: auto-generated types
	pass
