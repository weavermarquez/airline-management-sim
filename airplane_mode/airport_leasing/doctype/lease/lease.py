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
		period_length: DF.Literal["Monthly", "Quarterly"]
		periods: DF.Table[LeasePeriod]
		rental_rate: DF.Int
		start_date: DF.Date
		total_owing: DF.Currency
		total_paid: DF.Currency
	# end: auto-generated types
		from airplane_mode.airport_leasing.doctype.room.room import Room
		from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry

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

		room: Room = frappe.get_doc('Room', self.leasing_of)
		preconditions = [room_submitted, room_available, chronological_dates, minimum_one_period, backdated_recently]
		for pc in preconditions:
			if not pc():
				frappe.throw(pc.__doc__)

	def before_submit(self) -> None:
		"""Upon finalizing Lease, start the first Lease Period"""
		self.next_period()
		# TODO Set Room availability to Leased

	@property
	def total_owing(self) -> DF.Currency:
		periods = self.get_all_children('Lease Period')
		total_owing = sum(frappe.get_cached_value('Sales Invoice', 
							  period.invoice, 'grand_total') 
							  for period in periods if period.invoice)
		
		return total_owing

	@property
	def total_paid(self) -> DF.Currency:
		payments = self.get_all_children('Lease Payment')
		total_paid = sum(frappe.get_cached_value('Payment Entry', 
							  payment.payment_entry, 'paid_amount') 
							  for payment in payments if payment.payment_entry)
		return total_paid

	@property
	def outstanding_balance(self):
		return self.total_owing - self.total_paid

	@property
	def rental_rate(self):
		return frappe.get_cached_doc('Room', self.leasing_of).auto_rental_rate()

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================
	def next_period(self) -> None:
		"""At the end of this period, another period will begin."""
		from airplane_mode.airport_leasing.doctype.lease_period.lease_period import LeasePeriod
		next_period = LeasePeriod.next_period(self)
		self.append('periods', next_period)
		self.next_date = Lease.next_renew_date(self)
		# self.save()
		# This will cause the "Saved after opening Error.""


	def offboard() -> None:
		"""The current period will end at lease end. Begin offboarding."""
		pass


	def period_weeks(self) -> int:
		"""Get number of weeks for this lease's period length."""
		from typing_extensions import assert_never
		match self.period_length:
			case 'Monthly':
				return 4
			case 'Quarterly':
				return 12
			case _:
				assert_never(self.period_length)


	def latest_period(self) -> LeasePeriod:
		"""Return most recent Period based on latest start date"""
		if not self.periods:
			return None
		return max(self.periods, key=lambda period: period.start_date)


	def remind_tenant(self):
		pass

	@frappe.whitelist()
	def receive_payment(self, amount: DF.Currency, reference_no: DF.Data):
		"""When the tenant pays up on the Lease page, create a new Lease Payment."""
		from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment
		lease_payment = LeasePayment.new_payment(self, amount, reference_no)
		self.append('payments', lease_payment)
		self.save()

	# ==================== 
	# STATIC METHODS
	# ====================

	@staticmethod
	def total_weeks(start_date: DF.Date, end_date: DF.Date) -> float:
		days = frappe.utils.date_diff(end_date, start_date)
		return days / 7	

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
		# TODO New boolean variable to see if it has already been offboarded?
		expiring_soon = Lease.calculate_renewal_buffer(lease.end_date) <= today
		if expiring_soon:
			return lease.offboard()
		else:
			lease.next_period()


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
		renewal_buffer = frappe.utils.get_date_str(Lease.calculate_renewal_buffer(period_end))
		# frappe.utils.get_date_str()

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
