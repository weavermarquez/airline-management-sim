# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeaseInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		invoice_date: DF.Date | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sales_invoice: DF.Link | None
	# end: auto-generated types
	pass

	def validate(self) -> None:
		"""Submit the Transaction Record if not submitted."""
		if not self.sales_invoice:
			record = frappe.get_doc(self.sales_invoice)
			if not record.docstatus.is_submitted():
				record.submit()

	# TODO Better Throw Message.
	def on_trash(self) -> None:
		frappe.throw("Cannot delete Lease Invoices.")
