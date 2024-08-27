# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrewMember(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date_of_birth: DF.Date
		first_name: DF.Data
		full_name: DF.ReadOnly | None
		last_name: DF.Data | None
		name: DF.Int | None
		passport_id: DF.Data
	# end: auto-generated types

	def before_save(self):
		"""Sets the person's full name"""
		self.full_name = self.first_name if not self.last_name else f"{self.first_name} {self.last_name}"
