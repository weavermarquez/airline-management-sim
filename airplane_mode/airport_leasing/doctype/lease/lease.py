# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

from __future__ import annotations
import frappe
import json
from frappe.model.document import Document

class Lease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment
		from airplane_mode.airport_leasing.doctype.lease_period.lease_period import LeasePeriod
		from frappe.types import DF

		amended_from: DF.Link | None
		end_date: DF.Date
		leased_from: DF.Link
		leased_to: DF.Link
		leasing_of: DF.Link
		next_date: DF.ReadOnly | None
		outstanding_balance: DF.Currency
		payments: DF.Table[LeasePayment]
		periods: DF.Table[LeasePeriod]
		period_length: DF.Literal["Monthly", "Quarterly"]
		rental_rate: DF.Int
		sales_order: DF.Link | None
		start_date: DF.Date
	# end: auto-generated types
		from airplane_mode.airport_leasing.doctype.room.room import Room
		from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

	# TODO Probably add a function for server side validation to ensure that 
	# Lease Transactions cannot be deleted.

	# ==================== 
	# CONTROLLERS 
	# ====================

	def validate(self) -> None:
		def room_submitted() -> bool:
			"""The room being leased out should be finalized and submitted"""
			return room.docstatus.is_submitted()

		def room_available() -> bool:
			"""Room must be vacant when adding to any new leases."""
			return room.available()

		def chronological_dates() -> bool:
			"""Start date should be before end date"""
			return self.start_date < self.end_date

		def minimum_one_period() -> bool:
			"""Duration of lease should be at least 1 period. 
			Please choose a start date later than {minimum_end}"""
			minimum_end = frappe.utils.add_to_date(self.start_date, weeks=self.period_weeks())
			return minimum_end <= self.end_date

		# TODO Fix use dynamic docstrings.
		def backdated_recently() -> bool:
			"""If start date is backdated, it must have been within one period. 
			Please choose an end date later than {earliest_backdate}"""
			earliest_backdate = frappe.utils.add_to_date(frappe.utils.today(), weeks=-self.period_weeks())
			return earliest_backdate < self.start_date

		# self.autofill_rental_rate()
		room: Room = frappe.get_doc('Room', self.leasing_of)
		preconditions = [room_submitted, room_available, chronological_dates, minimum_one_period, backdated_recently]
		for pc in preconditions:
			if not pc():
				frappe.throw(pc.__doc__)

	# TODO Investigate if this is correct.
	def before_submit(self) -> None:
		"""Upon finalizing Lease, start the first Lease Period"""
		self.next_period()

		# self.set_next_date(self.start_date)
		# TODO Set Room availability to Leased

	def on_submit(self) -> None:
		pass

	def on_update_after_submit(self) -> None:
		pass

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	@frappe.whitelist()
	def update_transactions_on_next_date(doc: str) -> None:
		lease: Lease = frappe.get_doc(json.loads(doc))

		def triggers_today() -> bool:
			return lease.next_date == frappe.utils.today()
		def ends_today() -> bool:
			return lease.end_date == frappe.utils.today()
			
		if lease.docstatus.is_submitted() and triggers_today():
			lease.create_lease_transaction()

		# TODO Figure out what to do once the Lease ends.
		# if ends_today():
		# 	lease.cancel()

	@staticmethod
	def autorenew(doc: str) -> None:
		"""On next_date, prepare a new Lease Period or end the lease.
		The next_date can be within one period of the thingy."""
		lease: Lease = frappe.get_doc(json.loads(doc))
		today = frappe.utils.today()

		if any(lease.next_date != today, not lease.docstatus.is_submitted()):
			return
		
		# TODO unpaid deposit.
		unpaid = False
		expiring_soon = Lease.calculate_renewal_buffer(lease.end_date) <= today
		if expiring_soon:
			return lease.offboard()
		else:
			lease.next_period()


	def next_period(self) -> None:
		"""At the end of this period, another period will begin."""
		from airplane_mode.airport_leasing.doctype.lease_period.lease_period import LeasePeriod
		next_period = LeasePeriod.next_period(self)
		self.append('periods', next_period)
		self.next_date = Lease.next_renew_date(self)
		self.save()


	def offboard() -> None:
		"""The current period will end at lease end. Begin offboarding."""
		pass


	def period_weeks(self) -> int:
		"""Get number of weeks for this lease's period length."""
		return Lease.period_weeks(self.period_length)


	def latest_period(self) -> LeasePeriod:
		"""Return most recent Period based on latest start date"""
		if not self.periods:
			return None
		return max(self.periods, key=lambda period: period.start_date)


	def remind_tenant(self):
		pass

	# ==================== 
	# STATIC METHODS
	# ====================
	@staticmethod
	def period_weeks(period_length: str) -> int:
		"""Convert period_length to number of weeks."""
		from typing_extensions import assert_never
		match period_length:
			case 'Monthly':
				return 4
			case 'Quarterly':
				return 12
			case _:
				assert_never(period_length)


	@staticmethod
	def total_weeks(start_date: DF.Date, end_date: DF.Date) -> float:
		days = frappe.utils.date_diff(end_date, start_date)
		return days / 7	


	@staticmethod
	def new_payment_entry(lease: 'Lease', amount: float) -> PaymentEntry:
		"""Associate the newly user-created Payment Entry to a Lease Transaction"""
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry 

		sales_invoice = lease.latest_invoice()
		payment_entry: PaymentEntry = get_payment_entry('Sales Invoice', 
												  sales_invoice.name, 
												  party_amount=amount, 
												  reference_no = '23324', # TODO Fix Magic Number
												  reference_date=frappe.utils.today())
		return payment_entry
		# from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
		# payment_entry: PaymentEntry = get_payment_entry_against_invoice('Sales Invoice', sales_invoice.name, amount)

	@staticmethod
	def calculate_renewal_buffer(period_end: DF.Date) -> DF.Date:
		"""
		Calculate the date 14 days before the period ends.
		"""
		return frappe.utils.add_days(period_end, -14)

	@staticmethod
	def next_renew_date(lease: 'Lease') -> DF.Date:
		"""
		Calculate the next renewal date for the lease.

		The renewal date is set to the earlier of:
		1. The renewal buffer (14 days before the current period ends)
		2. Today's date (if we're already within the renewal buffer)
		3. The lease end date (to ensure we don't schedule renewals after the lease expires)
		"""
		latest_period = lease.latest_period()
		if not latest_period:
			return None

		today = frappe.utils.today()
		period_end = latest_period.end_date
		renewal_buffer = Lease.calculate_renewal_buffer(period_end)

		renewal_date = max(today, renewal_buffer)
		return min(lease.end_date, renewal_date)



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_filtered_child_rows(doctype, txt, searchfield, start, page_len, filters) -> list:
	"""Meant to be called by lease.js. Queries Invoices."""
	table = frappe.qb.DocType(doctype)
	query = (
		frappe.qb.from_(table)
		.select(
			table.name,
			# Concat("#", table.idx, ", ", table.item_code),
		)
		# .orderby(table.idx)
		.offset(start)
		.limit(page_len)
	)

	if filters:
		for field, value in filters.items():
			query = query.where(table[field] == value)

	# if txt:
	# 	txt += "%"
	# 	query = query.where(
	# 		((table.idx.like(txt.replace("#", ""))) | (table.item_code.like(txt))) | (table.name.like(txt))
	# 	)

	return query.run(as_dict=False)

@frappe.whitelist()
def send_payment_reminders() -> None:
	"""app.scheduled_tasks.update_database_usage"""
	def create_rent_reminder(self):
		pass
	pass
