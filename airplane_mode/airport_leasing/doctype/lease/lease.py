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
		discounted_rental_rate: DF.Currency
		end_date: DF.Date
		leased_from: DF.Link
		leased_to: DF.Link
		leasing_of: DF.Link
		next_date: DF.ReadOnly | None
		outstanding_balance: DF.Currency
		payments: DF.Table[LeasePayment]
		period_length: DF.Literal["Monthly", "Quarterly"]
		periods: DF.Table[LeasePeriod]
		rental_rate: DF.Currency
		start_date: DF.Date
		status: DF.Literal["Draft", "Submitted", "Active", "Overdue", "Offboarding", "Terminated", "Cancelled"]
		total_owing: DF.Currency
		total_paid: DF.Currency
	# end: auto-generated types

	# ==================== 
	# CONTROLLERS 
	# ====================

	def _validate_room_status(self, on_submit=False) -> None:
		"""When adding to a draft Lease, Room must not be Draft or Cancelled.
		When finalizing a Lease, the Room must be Available or Reserved."""
		from airplane_mode.airport_leasing.doctype.room.room import Room

		room = frappe.get_cached_doc('Room', self.leasing_of)
		required_status = Room.LEASE_DRAFT_ROOM_STATUS if not on_submit else Room.LEASE_SUBMIT_ROOM_STATUS

		self.validate_value('status', 'in', required_status, doc=room, raise_exception=True)
		# NOTE This doesn't work for docstatus 
		# as it is not explicitly defined in the DocType.

	@staticmethod
	def _validate_from_to(from_date, to_date) -> None:
		"""Ensure from_date is before to_date. Like doc.validate_from_to_dates, but works for non-fields."""
		if not (from_date and to_date):
			return

		if frappe.utils.date_diff(to_date, from_date) < 0:
			frappe.throw(
				("{0} must be after {1}").format(
					frappe.bold(to_date),
					frappe.bold(from_date),
				),
				frappe.exceptions.InvalidDates,
			)

	def _validate_minimum_one_period(self) -> bool:
		"""Ensure lease duration is at least one period."""
		minimum_end = frappe.utils.add_to_date(self.start_date, weeks=self.period_weeks())
		Lease._validate_from_to(minimum_end, self.end_date)

	def _validate_backdated_recently(self) -> bool:
		"""Check if start date is within one period of today."""
		earliest_backdate = frappe.utils.add_to_date(frappe.utils.today(), weeks=-self.period_weeks())
		Lease._validate_from_to(earliest_backdate, self.start_date)

	def validate(self) -> None:
		room: Room = frappe.get_doc('Room', self.leasing_of)

		self._validate_room_status()
		self.validate_from_to_dates('start_date', 'end_date')
		self._validate_minimum_one_period()
		self._validate_backdated_recently()

		self.set_status(update=True)

	def before_submit(self) -> None:
		"""Upon finalizing Lease, start the first Lease Period"""
		self._validate_room_status(on_submit=True)
		self.next_period()

	def on_submit(self) -> None:
		room = frappe.get_doc('Room', self.leasing_of)
		room.set_status(update=True)

	def on_update_after_submit(self) -> None:
		# NOTE You can also use: validate_table_has_rows
		room = frappe.get_doc('Room', self.leasing_of)
		room.set_status(update=True)
	
	def on_cancel(self) -> None:
		room = frappe.get_doc('Room', self.leasing_of)
		room.set_status(update=True)

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
	def rental_rate(self) -> float:
		return self.auto_rental_rate()

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

	def auto_rental_rate(self) -> float:
		"""Rental rates from most to least important priority:
		1. User-set discounted rate in Lease
		2. User-set override in Room
		3. User-set global rate in Airport Leasing Settings
		4. App-set global rate in Airport Leasing Settings"""

		if self.discounted_rental_rate:
			return self.discounted_rental_rate
		else:
			return frappe.get_cached_doc('Room', self.leasing_of).rental_rate

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


	def send_reminder(self, *, with_hooks: bool = False) -> None:
		"""Email tenant the monthly rent reminder. 

		:usage: send_reminder(with_hooks=True) :: call no-op version of itself 
			with self.run_method, triggering hooks.

		:usage: send_reminder() :: no-op
		:usage: send_reminder(with_hooks=False) :: no-op
		"""
		if with_hooks:
			self.run_method('send_reminder')

	@frappe.whitelist()
	def receive_payment(self, amount: DF.Currency, reference_no: DF.Data):
		"""When the tenant pays up on the Lease page, create a new Lease Payment."""
		# NOTE: Does this really need try / except?
		try:
			from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment
			lease_payment = LeasePayment.new_payment(self, amount, reference_no)
			self.append('payments', lease_payment)
			self.save(ignore_permissions=True)
			self.send_payment_receipt(with_hooks=True)
		except Exception as e:
			frappe.log_error(f"Failed to process payment: {str(e)}")
			frappe.throw("Failed to process payment. Please try again or contact support.")

	def send_payment_receipt(self, *, with_hooks: bool = False) -> None:
		"""Email a payment receipt to the tenant.

		:usage: send_payment_receipt(with_hooks=True) :: call no-op version of itself 
			with self.run_method, triggering hooks.

		:usage: send_payment_receipt() :: no-op
		:usage: send_payment_receipt(with_hooks=False) :: no-op
		"""
		if with_hooks:
			self.run_method('send_payment_receipt')

	def set_status(self, *, status=None, update=False, update_modified=True) -> None:
		"""Modify lease status based on child periods and end_date.

		Status values:
		- Draft: On create and before submit.
		- Active: Lease Period Invoices are in good standing
		- Overdue: One or more Invoices are not in good standing -- considered Overdue.
		- Offboarding: Lease end_date is within 2 weeks.
		- Terminated: Lease end_date is today, and invoices are in good standing.
		- Cancelled: Lease end_date is today, and invoices are not in good standing.

		- Maintenance: Room is under maintenance
		- Occupied: Room has active (submitted) leases
		- Reserved: Room has draft leases
		- Available: Room has no leases and is not under maintenance
		
		Args:
			update (bool): If True, updates the status in the database
		"""
		if not self.docstatus.is_submitted():
			if status:
				self.status = status
			return

		if any(period.status.startswith('Overdue') for period in self.periods):
			self.status = "Overdue"
		else:
			self.status = "Active"

	 	# TODO Move offboarding logic here if needed
		# expiring_soon = Lease.calculate_renewal_buffer(lease.end_date) <= today
		# if lease.status == 'Offboarding' and lease.end_date == today:
		# 	return lease.set_status(status='Terminated', update=True)
		# elif expiring_soon:
		# 	return lease.set_status(status='Offboarding', update=True)
		if status:
			self.status = status

		frappe.log_error(f'set_status({self.status}, {status}, {update})')
		if update:
			self.db_set("status", self.status, update_modified=update_modified, notify=True, commit=True)


	# ==================== 
	# STATIC METHODS
	# ====================

	@staticmethod
	def total_weeks(start_date: DF.Date, end_date: DF.Date) -> float:
		days = frappe.utils.date_diff(end_date, start_date)
		return days / 7	
	
	@staticmethod
	def retrieve_doc(doc: str) -> 'Lease':
		return frappe.get_doc(json.loads(doc))

	@staticmethod
	def autorenew(doc: (str | Lease)) -> None:
		""" On next_date, prepare a new Lease Period or end the lease.
		The next_date can be within one period of the thingy.
		
		Takes in either a Lease instance or its JSON representation.
		"""
		if isinstance(doc, str):
			lease: Lease = Lease.retrieve_doc(doc)
		else:
			lease = doc

		today = frappe.utils.today()

		lease.set_status(update_modified=False)

		# NOTE I can pre-filter all the leases in the daily scan, so this may be redundant.
		if any((lease.next_date != today, lease.docstatus.is_draft(), lease.docstatus.is_cancelled())):
			return
		
		ends_today = lease.end_date == today
		expiring_soon = Lease.calculate_renewal_buffer(lease.end_date) <= today

		if ends_today:
			# TODO Handle offboarding logic here if needed
			return lease.set_status(status='Terminated', update=True)
		elif expiring_soon:
			return lease.set_status(status='Offboarding', update=True)
		else:
			return lease.next_period()


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

def autorenew_daily() -> None:
	"""Run autorenew on all Submitted leases daily"""
	pluck = 'name'
	filters = [
		["docstatus", '=', 1], 
		["next_date", '=', frappe.utils.today()],
	]

	for lease_name in frappe.get_all("Lease", pluck=pluck, filters=filters):
		lease: Lease = frappe.get_doc('Lease', lease_name)
		Lease.autorenew(lease)

def send_reminder_monthly() -> None:
	"""Check lease rent reminders to be sent monthly"""
	enabled = frappe.get_single('Airport Leasing Settings').enable_payment_reminders
	if not enabled:
		return

	pluck = 'name'
	filters = [
		["docstatus", '=', 1], 
		# ['outstanding_balance', ">", 0], 
		# NOTE I could use status == Overdue. But frankly just every active lease is fine.
	]

	for lease_name in frappe.get_all("Lease", pluck=pluck, filters=filters):
		lease: Lease = frappe.get_doc('Lease', lease_name)
		lease.send_reminder(with_hooks=True)