# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

from __future__ import annotations
import frappe
from frappe.model.document import Document


class LeasePeriod(Document):
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
		pass

	@property
	def status(self) -> str:
		return frappe.get_cached_value('Sales Invoice', self.invoice, 'status')

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	@staticmethod
	def next_period(lease) -> 'LeasePeriod':
		"""
		Begin a new Lease Period and send an invoice.

		This method creates a new Lease Period document and generates a corresponding Sales Invoice.
		It calculates the start and end dates for the new period, creates a new invoice item,
		and associates it with a new Sales Invoice. Finally, it creates a new Lease Period
		document linked to the generated invoice.

		Note:
		- This method should be called when starting a new lease or when a current period is ending.
		"""

		# TODO Implement logic to limit the next period until end of lease end date.
		def get_period_start_date():
			"""
			Start date is determined by either 
			- the lease start date (for the first period);
		  	- ; or the day after the end of the last period.
			"""
			if not lease.periods:
				return lease.start_date
			else:
				last_period = lease.latest_period()
				return frappe.utils.add_days(last_period.end_date, 1)

		def get_period_end_date():
			"""
			End date:
			- calculated based on the lease's period length (e.g., monthly, quarterly),
			- cannot exceed the lease's end date.
			"""
			end = frappe.utils.add_to_date(period_start_date, weeks=period_duration)
			return min(end, lease.end_date)

		room: str = lease.leasing_of
		company: str = lease.leased_from
		customer: str = frappe.get_value('Shop', lease.leased_to, 'owned_by')

		period_start_date = get_period_start_date()
		period_duration = lease.period_weeks()
		period_end_date = get_period_end_date()

		item = LeasePeriod.new_invoice_item(room, period_start_date, period_duration)
		invoice = LeasePeriod.new_sales_invoice(item, company, customer)

		lease_period = frappe.new_doc('Lease Period',
								start_date = period_start_date,
								end_date = period_end_date, 
								invoice = invoice.name)
		return lease_period


	@staticmethod
	def new_invoice_item(room: str, start_date: 'DF.Date', weeks: float) -> SalesInvoiceItem:
		"""Allocate the Room for the Period's duration"""
		from airplane_mode.airport_leasing.doctype.room.room import Room
		item = frappe.new_doc("Sales Invoice Item",
					item_code = room,
					delivery_date = start_date,
					qty = weeks,
					uom = Room.UOM)
		# NOTE I think I need to manually set the price for this thing?
		return item


	@staticmethod
	def new_sales_invoice(item: SalesInvoiceItem, company: str, customer: str) -> SalesInvoice:
		"""Bill customer for upcoming period"""
		# TODO The due_date gives 2wk buffer after first period
		# But is due on the day the next period begins.
		sales_invoice: SalesInvoice = frappe.new_doc('Sales Invoice', 
			customer = customer,
			company = company,
			posting_date = frappe.utils.today(),
			due_date = frappe.utils.add_days(frappe.utils.today(), 14),
			items = [ item ],
		)
		return sales_invoice.submit()

		# Does customer need Payment Terms set up?
