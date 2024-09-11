# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Airport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		city: DF.Data
		code: DF.Data
		country: DF.Data
	# end: auto-generated types
	pass

	def uwu(self):
		return "uwu"

	def owo(self):
		return "owo"

	def awa(self):
		return "awa"