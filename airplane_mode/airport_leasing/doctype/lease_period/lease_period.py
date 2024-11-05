# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

from __future__ import annotations
import frappe
from frappe.model.document import Document

from typing import TypeAlias

# Type aliases for better readability
SalesInvoice: TypeAlias = 'frappe.types.Document'
SalesInvoiceItem: TypeAlias = 'frappe.types.Document'


class LeasePeriod(Document):
	"""
	Represents a period of time for which a lease is active.
	Handles the creation and management of lease periods including invoice generation.
	"""
	INVOICE_BUFFER_DAYS = 14
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		end_date: DF.Date | None
		invoice: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		start_date: DF.Date | None
		status: DF.ReadOnly | None
	# end: auto-generated types
	pass

	def validate(self) -> None:
		"""Validate lease period dates and invoice"""
		if self.start_date and self.end_date and self.start_date > self.end_date:
			frappe.throw('Start date cannot be after end date')
		
		if self.invoice and not frappe.db.exists('Sales Invoice', self.invoice):
			frappe.throw('Invalid invoice reference')

	@property
	def status(self) -> str:
		"""Get the current status of the associated invoice"""
		if not self.invoice:
			return 'Draft'
		return frappe.get_cached_value('Sales Invoice', self.invoice, 'status') or 'Draft'

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	@staticmethod
	def next_period(lease) -> 'LeasePeriod':
		"""Begin a new Lease Period and send an invoice."""
		dates = LeasePeriod.calculate_period_dates(lease)
		invoice = LeasePeriod.create_period_invoice(lease, dates)
		
		return frappe.new_doc(
			'Lease Period', 
			start_date=dates['start_date'],
			end_date=dates['end_date'],
			invoice=invoice.name
		)

	@staticmethod
	def calculate_period_dates(lease) -> dict:
		"""Calculate start and end dates for the next period.
		
		Returns:
			dict: Contains 'start_date' and 'end_date'
		"""
		start_date = LeasePeriod._get_period_start_date(lease)
		end_date = LeasePeriod._get_period_end_date(lease, start_date)
		
		return {
			'start_date': start_date,
			'end_date': end_date
		}

	@staticmethod
	def _get_period_start_date(lease) -> str:
		"""Determine the start date for the next period."""
		if not lease.periods:
			return lease.start_date
		
		last_period = lease.latest_period()
		return frappe.utils.add_days(last_period.end_date, 1)

	@staticmethod
	def _get_period_end_date(lease, start_date: str) -> str:
		"""Calculate the end date based on period length and lease constraints."""
		period_end = frappe.utils.add_to_date(
			start_date, 
			weeks=lease.period_weeks()
		)
		return min(period_end, lease.end_date)

	@staticmethod
	def create_period_invoice(lease, dates: dict) -> SalesInvoice:
		"""Create and submit invoice for the period."""
		room = lease.leasing_of
		company = lease.leased_from
		customer = frappe.get_value('Shop', lease.leased_to, 'owned_by')
		
		item = LeasePeriod.new_invoice_item(
			room=room,
			start_date=dates['start_date'],
			weeks=lease.period_weeks()
		)
		
		return LeasePeriod.new_sales_invoice(
			item=item,
			company=company,
			customer=customer
		)

	@staticmethod
	def new_invoice_item(room: str, start_date: DF.Date, weeks: float) -> 'SalesInvoiceItem':
		"""
		Create a new invoice item for room lease.
		
		Args:
			room: Room identifier
			start_date: Period start date
			weeks: Duration in weeks
			
		Returns:
			SalesInvoiceItem: New invoice item document
		"""
		from airplane_mode.airport_leasing.doctype.room.room import Room
				
		if not frappe.db.exists('Room', room):
			frappe.throw(f'Room {room} does not exist')

		item = frappe.new_doc("Sales Invoice Item",
					item_code = room,
					delivery_date = start_date,
					qty = weeks,
					uom = Room.UOM)

		# Get rate from Room document or pricing rules
		item.rate = frappe.get_value('Room', room, 'rate') # or 0
		return item


	@staticmethod
	def new_sales_invoice(item: SalesInvoiceItem, company: str, customer: str) -> SalesInvoice:
		"""Create and submit a new sales invoice for a lease period.

		Args:
			item: The invoice item for the room rental
			company: Company issuing the invoice
			customer: Customer being billed
			
		Returns:
			SalesInvoice: The submitted sales invoice document
			
		Note:
			The invoice due date is set to INVOICE_BUFFER_DAYS after the posting date.
			For the first period this gives a 2 week buffer, but subsequent periods
			are due on the start date of the next period.
		"""
		# NOTE The due_date gives 2wk buffer after first period
		# But is due on the day the next period begins.
		sales_invoice: SalesInvoice = frappe.new_doc('Sales Invoice', 
			customer = customer,
			company = company,
			posting_date = frappe.utils.today(),
			due_date = frappe.utils.add_days(frappe.utils.today(), LeasePeriod.INVOICE_BUFFER_DAYS),
			items = [ item ],
		)
		return sales_invoice.submit()

		# Does customer need Payment Terms set up?
