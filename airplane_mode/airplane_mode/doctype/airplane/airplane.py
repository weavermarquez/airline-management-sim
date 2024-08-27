# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Airplane(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		airline: DF.Link
		capacity: DF.Int
		initial_audit_completed: DF.Check
		model: DF.Data
	# end: auto-generated types
	pass
