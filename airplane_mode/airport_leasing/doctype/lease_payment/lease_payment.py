# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# from __future__ import annotations
import frappe
from frappe.model.document import Document


class LeasePayment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payment_date: DF.Date | None
		payment_entry: DF.Link | None
	# end: auto-generated types
	pass

	# TODO Better Throw Message.
	def on_trash(self) -> None:
		frappe.throw("Cannot delete Lease Payments.")


	@staticmethod
	def new_payment(lease: 'Lease', amount, reference_no) -> 'LeasePayment':
		from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment

		payment_entry = LeasePayment.new_payment_entry(lease, amount, reference_no)
		lease_payment: LeasePayment = frappe.new_doc('Lease Payment', payment_entry=payment_entry.name)
		return lease_payment


	@staticmethod
	def new_payment_entry(lease: 'Lease', amount: float, reference_no: 'DF.Data') -> 'PaymentEntry':
		"""Associate the newly user-created Payment Entry to a Lease Transaction"""
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry 

		sales_invoice_name = lease.latest_period().invoice
												#   reference_no=reference_no,

		payment_entry: PaymentEntry = get_payment_entry('Sales Invoice', 
												  sales_invoice_name,
												  party_amount=amount, 
												  reference_date=frappe.utils.today())

		payment_entry.reference_no = reference_no
		return payment_entry.submit()
		# from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
		# payment_entry: PaymentEntry = get_payment_entry_against_invoice('Sales Invoice', sales_invoice.name, amount)
