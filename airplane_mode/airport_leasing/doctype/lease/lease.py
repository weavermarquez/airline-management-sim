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
			minimum_end = frappe.utils.add_to_date(self.start_date, weeks=self.get_frequency())
			return minimum_end <= self.end_date

		# TODO Fix use dynamic docstrings.
		def backdated_recently() -> bool:
			"""If start date is backdated, earliest permitted date is within one period before today.
			Please choose an end date later than {earliest_backdate}"""
			earliest_backdate = frappe.utils.add_to_date(frappe.utils.today(), weeks=-self.get_frequency())
			return earliest_backdate < self.start_date

		# self.autofill_rental_rate()
		room: Room = frappe.get_doc('Room', self.leasing_of)
		preconditions = [room_submitted, room_available, chronological_dates, minimum_one_period, backdated_recently]
		for pc in preconditions:
			if not pc():
				frappe.throw(pc.__doc__)

	# TODO Investigate if this is correct.
	def before_submit(self) -> None:
		"""While finalizing Lease, create a Sales Order and recurring Sales Invoice"""
		self.set_sales_order()
		self.append_sales_invoice()

		# self.set_next_date(self.start_date)
		# Hmm? What does this do?
		# postdated, must wait until next_date to create a transaction.
		# else post-dated
		# TODO Set Room availability to Leased

	def on_submit(self) -> None:
		pass

	def on_update_after_submit(self) -> None:
		pass
		# def last_period() -> bool:
		# 	return self.next_date > self.end_date

		# if last_period():
		# 	return
		# read only:
		# item, next_date
		# transactions

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	def set_next_date(self, date: DF.Date) -> None:
		self.next_date = date

	# TODO Issue #7
	def set_sales_order(self) -> None:
		customer: str = frappe.get_value('Shop', self.leased_to, 'owned_by')
		company = self.leased_from 
		
		item = Lease.new_item(self.room, self.start_date, self.end_date)
		self.sales_order = Lease.new_sales_order(item, company, customer)


	def append_sales_invoice(self) -> None:
		sales_invoice = Lease.new_sales_invoice(self.sales_order)
		self.invoices.append(sales_invoice)


	def append_payment_entry(self) -> None:
		payment_entry = Lease.new_payment_entry(self)
		self.payments.append(payment_entry)


	# TODO Set default rental rate logic in Room as well
	def autofill_rental_rate(self) -> None:
		"""When a Sales Order is created, the price is determined by this 
		order of priority for rental rates, from most to least important:
		1. Pre-existing or user-set rate
		2. user-set rate in Room
		3. user-set rate in Airport Leasing Settings
		4. default system rate in Airport Leasing Settings"""

		if self.rental_rate:
			return

		new_rate = frappe.get_doc('Airport Leasing Settings').default_rental_rate

		room_rental_rate = frappe.get_value('Room', self.leasing_of, 'default_rental_rate')
		if room_rental_rate:
			new_rate = room_rental_rate

		self.rental_rate = new_rate

	def get_frequency(self) -> int:
		"""Get number of weeks for this lease's invoice frequency."""
		return Lease.period_weeks(self.invoice_frequency)


	def latest_invoice(self) -> SalesInvoice:
		"""Return most recent Sales Invoice"""
		return frappe.get_doc('Sales Invoice', self.invoices[-1].invoice)


	# def frequency_payment_template(self) -> str:
	# 	template = f"Airport {self.invoice_frequency}"
	# 	if not frappe.db.exists('Payment Terms Template', template):
	# 		frappe.throw('Airport Leasing fixtures for Payment Terms Templates are missing.')
	# 	return template


	# def create_rent_reminder(self):
	# 	pass


	# def save_move_next_date(self) -> None:
	# 	def last_period() -> bool:
	# 		return self.next_date > self.end_date
		
	# 	months = self.frequency_in_months()
	# 	# self.set('next_date', frappe.utils.add_months(self.next_date, months))
	# 	self.next_date = frappe.utils.add_months(self.next_date, months)
	# 	# scope when declared; value when evaluated

	# 	# If next_date is after end_date, add a special warning?

	# 	if last_period():
	# 		return
	# 	self.save()
	# 	self.notify_update()


	# ==================== 
	# STATIC METHODS
	# ====================
	@staticmethod
	def period_weeks(invoice_frequency: str) -> int:
		"""Convert invoice_frequency to number of weeks."""
		from typing_extensions import assert_never
		match invoice_frequency:
			case 'Monthly':
				return 4
			case 'Quarterly':
				return 12
			case _:
				assert_never(invoice_frequency)


	@staticmethod
	def new_item(room: str, start_date: DF.Date, end_date: DF.Date) -> SalesOrderItem:
		item = frappe.new_doc("Sales Order Item",
					item_code = room,
					delivery_date = start_date,
					qty = Lease.duration_weeks(start_date, end_date),
					uom = Room.UOM)
		return item


	@staticmethod
	def total_weeks(start_date: DF.Date, end_date: DF.Date) -> float:
		days = frappe.utils.date_diff(end_date, start_date)
		return days / 7	


	@staticmethod
	def new_sales_order(item: SalesOrderItem, company: str, customer: str) -> SalesOrder:
		"""Create a new Sales Order representing the entire duration of the Lease."""
		from airplane_mode.airport_leasing.doctype.room.room import Room

		sales_order: SalesOrder = frappe.new_doc('Sales Order', 
			customer = customer,
			company = company,
			transaction_date = frappe.utils.today(),
			items = [ item ],
			# TODO I think I need to manually set the price for this thing?
		)
		return sales_order


	@staticmethod
	def new_sales_invoice(sales_order: str) -> SalesInvoice:
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
		# TODO Confirm if it needs so.docstatus == 1
		return make_sales_invoice(sales_order)  # needs so.docstatus == 1

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

# @frappe.whitelist()
# def send_payment_reminders() -> None:
# 	"app.scheduled_tasks.update_database_usage"	
# 	def create_rent_reminder(self):
# 		pass
# 	pass


# def html_template():
# 	return '<h1>OwO</h1>'

# def notification_fixtures():
# 	"""TODO Fixtures for Sales Invoice Notifications """
# 	# https://docs.erpnext.com/docs/user/manual/en/notifications 
# 	# TODO Figure out what method?
# 	# TODO Understand what "Custom" means as it's not well clarified on erpnext wiki
# 	# Especially in conjunction with self.run_notifcations()

# 	notifications_enabled = 1 # frappe.get_doc('Airport Leasing Settings').notifications_enabled
# 	conditions = "doc.status in ('Unpaid', 'Partly Paid', 'Overdue')"
# 	message = html_template()

# 	# TODO Create Subject, HTML Template
# 	reminder_notif = frappe.new_doc('Notification',
# 				__newname = 'Outstanding airport lease payment reminder',
# 				channel = 'Email',
# 				enabled = notifications_enabled,
# 				subject = '',
# 				event = 'Method',
# 				document_type = 'Sales Invoice',
# 				is_standard = 1,
# 				module = 'Airport Leasing',
# 				condition = conditions,
# 				send_to_all_assignees = 0,
# 				message_type = 'HTML',
# 				message = message,
# 				attach_print = 0,
# 				recipients = [ {'receiver_by_document_field': 'contact_email'} ],
# 				# TODO I should test if this method of defining children works.
# 				)

# 	notifications_enabled = 1 # frappe.get_doc('Airport Leasing Settings').notifications_enabled
# 	conditions = "doc.status in ('Unpaid', 'Partly Paid', 'Overdue')"
# 	message = html_template()
# 	# TODO Create Subject, HTML Template
# 	receipt_notif = frappe.new_doc('Notification',
# 				__newname = 'Airport lease payment receipt',
# 				channel = 'Email',
# 				enabled = notifications_enabled,
# 				subject = '',
# 				event = 'Method',
# 				document_type = 'Payment Entry',
# 				is_standard = 1,
# 				module = 'Airport Leasing',
# 				condition = conditions,
# 				send_to_all_assignees = 0,
# 				message_type = 'HTML',
# 				message = message,
# 				attach_print = 0,
# 				# recipients = [ {'receiver_by_document_field': 'contact_email'} ],
# 				# TODO Find what 
# 				)
# 	pass

# def payment_fixtures():
# 	"""TODO Fixtures for Payment Term"""
# 	# https://docs.erpnext.com/docs/user/manual/en/payment-terms
# 	# https://docs.erpnext.com/docs/user/manual/en/sales-invoice
# 	monthly_term = frappe.new_doc('Payment Term',
# 				payment_term_name = 'Airport 2 Weeks',
# 				invoice_portion = 100,
# 				due_date_based_on = 'Day(s) after invoice date',
# 				credit_days = 14,
# 				description = "Fully paid by the 2nd week",
# 				)
# 	monthly_template = frappe.new_doc('Payment Terms Template',
# 				template_name = 'Airport Monthly',
# 				terms = [ monthly_term ],
# 				)


# 	quarterly_a = frappe.new_doc('Payment Term',
# 				payment_term_name = 'Airport 50 First Month',
# 				invoice_portion = 50,
# 				due_date_based_on = 'Month(s) after the end of the invoice month',
# 				credit_days = 1,
# 				description = "Airport Within 1st Month",
# 				)
# 	quarterly_b = frappe.new_doc('Payment Term',
# 				payment_term_name = 'Airport 50 Second Month',
# 				invoice_portion = 50,
# 				due_date_based_on = 'Month(s) after the end of the invoice month',
# 				credit_months = 2,
# 				description = "Airport Within 2nd Month",
# 				)
# 	quarterly_template = frappe.new_doc('Payment Terms Template',
# 				template_name = 'Airport Quarterly',
# 				allocate_payment_based_on_payment_terms = 1,
# 				terms = [ quarterly_a, quarterly_b ],
# 				)

# def minimal_customer():
# 	customer_types = ['Company', 'Individual', 'Proprietorship', 'Partnership']
# 	frappe.new_doc('Customer',
# 				customer_name = '',
# 				customer_type = 'Company', 


# 				)
# 	return