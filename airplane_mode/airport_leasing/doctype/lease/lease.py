# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

from __future__ import annotations
import frappe
import json
from frappe.model.document import Document
from typing import Optional, List, Dict, Any, Tuple, Callable
from typing import (TypeAlias, TYPE_CHECKING)

if TYPE_CHECKING:
	from airplane_mode.airport_leasing.doctype.room.room import Room
	# from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
	# Type aliases for better readability
	# Lease: TypeAlias = 'frappe.types.Document'
	# Room: TypeAlias = 'frappe.types.Document'

class Lease(Document):
	RENEWAL_BUFFER_DAYS = 14
	PERIOD_WEEKS = {
		'Monthly': 4,
		'Quarterly': 12
	}
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
		status: DF.Literal["Draft", "Submitted", "Active", "Overdue", "Cancelled"]
		total_owing: DF.Currency
		total_paid: DF.Currency
	# end: auto-generated types

	# ==================== 
	# CONTROLLERS 
	# ====================
	def _validate_room_submitted(self) -> bool:
		"""The room being leased out should be finalized and submitted"""
		message = "The room being leased out should be finalized and submitted"
		is_valid = frappe.get_value('Room', self.leasing_of, 'docstatus') == 1
		return is_valid, message

	def _validate_room_status(self, on_submit=False) -> bool:
		"""Room must be valid when adding to any new leases."""
		message = "Room must be valid when adding to any new leases."
		valid_status = Room.LEASE_DRAFT_ROOM_STATUS if not on_submit else Room.LEASE_SUBMIT_ROOM_STATUS
		is_valid = frappe.get_value('Room', self.leasing_of, 'status') in valid_status
		return is_valid, message

	def _validate_dates(self) -> bool:
		"""Start date should be before end date."""
		message = "Start date should be before end date."
		is_valid = self.start_date < self.end_date
		return is_valid, message

	def _validate_minimum_one_period(self) -> bool:
		"""Check if duration is at least one period."""
		minimum_end = frappe.utils.add_to_date(self.start_date, weeks=self.period_weeks())
		is_valid = minimum_end <= self.end_date
		message = f"Duration of lease should be at least 1 period. Please choose a start date later than {minimum_end}"
		return is_valid, message

	def _validate_backdated_recently(self) -> bool:
		"""Check if start date is within one period of today."""
		earliest_backdate = frappe.utils.add_to_date(frappe.utils.today(), weeks=-self.period_weeks())
		is_valid = earliest_backdate < self.start_date
		message = f"If start date is backdated, it must have been within one period. Please choose an end date later than {earliest_backdate}"
		return is_valid, message 

	def validate(self) -> None:
		room: Room = frappe.get_doc('Room', self.leasing_of)

		validations = [
			self._validate_room_submitted,
			self._validate_room_status,
			self._validate_dates,
			self._validate_minimum_one_period,
			self._validate_backdated_recently,
		]

		for validator in validations:
			is_valid, message = validator()
			if not is_valid:
				frappe.throw(message)

		self.set_status(update=True)

	def before_submit(self) -> None:
		"""Upon finalizing Lease, start the first Lease Period"""
		is_valid, message = self._validate_room_status(on_submit=True)
		if not is_valid:
			frappe.throw(message)
		self.next_period()

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
		periods = self.get_all_children('Lease Period')
		total_outstanding = sum(frappe.get_cached_value('Sales Invoice', 
							  period.invoice, 'outstanding_amount') 
							  for period in periods if period.invoice)
		
		return total_outstanding
		# return self.total_owing - self.total_paid

	@property
	def rental_rate(self):
		return frappe.get_cached_doc('Room', self.leasing_of).auto_rental_rate()

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================
	def next_period(self) -> None:
		"""Upon finalizing the lease, or two weeks before end of the most recent period, another period will begin."""
		from airplane_mode.airport_leasing.doctype.lease_period.lease_period import LeasePeriod
		next_period = LeasePeriod.next_period(self)
		self.append('periods', next_period)
		self.next_date = Lease.next_renew_date(self)
		# self.save()
		# This will cause the "Saved after opening Error.""


	def offboard(self) -> None:
		"""The current period will end at lease end. Begin offboarding."""
		self.offboard = True
		self.save()


	def period_weeks(self) -> int:
		"""Get number of weeks for this lease's period length."""
		return self.PERIOD_WEEKS[self.period_length]

	def unpaid_periods(self) -> list[dict]:
		if not self.periods:
			return None

		def unpaid(period) -> bool:
			return period.status.startswith(('Overdue', 'Partly Paid', 'Unpaid'))

		return list(filter(unpaid, self.periods))

	def latest_period(self, *, filter_unpaid = False) -> Optional[LeasePeriod]:
		"""Return most recent Period based on latest start date.
		Args:
		filter_unpaid: If True, only consider unpaid periods
	
		Returns:
		The most recent LeasePeriod or None if no periods exist
		"""
		if not self.periods:
			return None
		
		periods = self.unpaid_periods() if filter_unpaid else self.periods
		return max(periods, key=lambda period: period.start_date) if periods else None


	def remind_tenant(self):
		pass

	@frappe.whitelist()
	def receive_payment(self, amount: DF.Currency, reference_no: DF.Data):
		"""When the tenant pays up on the Lease page, create a new Lease Payment."""
		# NOTE: Does this really need try / except?
		try:
			from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment
			lease_payment = LeasePayment.new_payment(self, amount, reference_no)
			self.append('payments', lease_payment)
			self.save()
		except Exception as e:
			frappe.log_error(f"Failed to process payment: {str(e)}")
			frappe.throw("Failed to process payment. Please try again or contact support.")

	def set_status(self, update=False, update_modified=True) -> None:
		if not self.docstatus.is_submitted():
			return

		if any(period.status.startswith('Overdue') for period in self.periods):
			self.status = "Overdue"
		else:
			self.status = "Active"

		if update:
			self.db_set("status", self.status, update_modified=update_modified)


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

		lease.set_status(update=True, update_modified=False)

		if any(lease.next_date != today, lease.docstatus.is_draft(), lease.docstatus.is_cancelled()):
			return
		
		expiring_soon = Lease.calculate_renewal_buffer(lease.end_date) <= today
		if lease.offboarded:
			# TODO Do something? Or not?
			return
		elif expiring_soon:
			lease.offboard()
			return
		else:
			lease.next_period()


	@staticmethod
	def calculate_renewal_buffer(period_end: DF.Date) -> DF.Date:
		"""
		Calculate the date RENEWAL_BUFFER_DAYS before the period ends.
		"""
		return frappe.utils.add_days(period_end, -Lease.RENEWAL_BUFFER_DAYS)


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
