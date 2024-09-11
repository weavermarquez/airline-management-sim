# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

from airplane_mode.airport_leasing.doctype.room.room import Room

from erpnext.selling.doctype.sales_order.sales_order import ( make_sales_invoice, SalesOrder )
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.accounts.doctype.payment_entry.payment_entry import ( get_payment_entry, PaymentEntry )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF
	from frappe.model.docstatus import DocStatus
	pass

class Lease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from airplane_mode.airport_leasing.doctype.lease_transaction.lease_transaction import LeaseTransaction
		from frappe.types import DF

		amended_from: DF.Link | None
		end_date: DF.Date
		invoice_frequency: DF.Literal["Monthly", "Quarterly"]
		item: DF.Link | None
		leased_from: DF.Link
		leased_to: DF.Link
		leasing_of: DF.Link
		next_date: DF.ReadOnly | None
		rental_rate: DF.Int
		start_date: DF.Date
		transactions: DF.Table[LeaseTransaction]
	# end: auto-generated types
	pass

	UOM = 'Week'

	def frequency_in_days(self) -> int:
		return 30 * self.frequency_in_months()

	def frequency_in_weeks(self) -> int:
		return 4 * self.frequency_in_months()

	def frequency_in_months(self) -> int:
		"""Comprehensively converts invoice_frequency to month durations."""
		from typing_extensions import assert_never
		match self.invoice_frequency:
			case 'Monthly':
				return 1
			case 'Quarterly':
				return 3
			case _:
				assert_never(self.invoice_frequency)

	def frequency_payment_template(self) -> str:
		template = f"Airport {self.invoice_frequency}"
		if not frappe.db.exists('Payment Terms Template', template):
			frappe.throw('Airport Leasing fixtures for Payment Terms Templates are missing.')
		return template


	def validate(self) -> None:
		# leasing_of
		def room_submitted() -> bool:
			"""The room being leased out should be finalized and submitted"""
			return room.docstatus.is_submitted()
			# return frappe.get_value('Room', self.leasing_of, 'docstatus') == DocStatus.is_submitted()

		def room_available() -> bool:
			"""Room must be vacant when adding to any new leases."""
			return room.available()

		def chronological_dates() -> bool:
			"""Start date should be before end date"""
			return self.start_date < self.end_date

		def minimum_one_period() -> bool:
			"""Duration of lease should be at least 1 period. 
			Please choose a start date later than {minimum_end}"""
			minimum_end = frappe.utils.add_months(self.start_date, self.frequency_in_months())
			return minimum_end <= self.end_date

		def backdated_recently() -> bool:
			"""If start date is backdated, earliest permitted date is within one period before today.
			Please choose an end date later than {earliest_backdate}"""
			# earliest_backdate = frappe.utils.add_months(frappe.utils.today(), -self.frequency_in_months())
			return earliest_backdate < self.start_date
			# NOTE Damn, docstrings can't be f-strings. This is one downside.

		room: Room = frappe.get_doc('Room', self.leasing_of)
		preconditions = [room_submitted, room_available, chronological_dates, minimum_one_period]
		for pc in preconditions:
			if not pc():
				frappe.throw(pc.__doc__)


		earliest_backdate = frappe.utils.add_months(frappe.utils.today(), -self.frequency_in_months())
		if not backdated_recently():
			frappe.throw(f"{backdated_recently.__doc__}\nChoose a date later than {earliest_backdate}")
		# self.autofill_rental_rate()

		# leased_to a Shop, which has a Customer
		# leased_from a Company

	# def autofill_rental_rate(self) -> None:
	# 	"""When a Sales Order is created, the price is determined by this 
	# 	order of priority for rental rates, from most to least important:
	# 	1. Pre-existing or user-set rate
	# 	2. user-set rate in Room
	# 	3. user-set rate in Airport Leasing Settings
	# 	4. default system rate in Airport Leasing Settings"""
	# 	# TODO Set default rental rate logic in Room as well

	# 	if self.rental_rate:
	# 		return

	# 	new_rate = frappe.get_doc('Airport Leasing Settings').default_rental_rate

	# 	room_rental_rate = frappe.get_value('Room', self.leasing_of, 'default_rental_rate')
	# 	if room_rental_rate:
	# 		new_rate = room_rental_rate

	# 	self.rental_rate = new_rate

	def before_submit(self) -> None:
		self.next_date = self.start_date
		# postdated, must wait until next_date to create a transaction.

	def on_submit(self) -> None:
		# TODO Set Room availability to Leased
		if self.start_date <= frappe.utils.today():  # back-dated or today
			# we must explicitly invoke create_lease_transaction() so next_date is in future
			self.create_lease_transaction()
		self.create_lease_transaction()
		# TODO Remove this later
		# else post-dated

	def on_update_after_submit(self) -> None:
		def last_period() -> bool:
			return self.next_date > self.end_date

		if last_period():
			return
		# read only:
		# item, next_date
		# transactions

	def create_lease_transaction(self) -> None:
		frappe.errprint('Wal: creating Sales Order~')
		so = self.create_submit_sales_order()

		frappe.errprint('Wal: creating Sales Invoice~')
		si = self.create_submit_sales_invoice(so)
		# pe = self.create_save_payment_entry(si)
		pe = None
		# self.run_notifications()

		frappe.errprint('Wal: Appending to transactions~')
		self.save_append_to_transactions(so, si, pe)
		self.save_move_next_date()
		self.notify_update()

		frappe.msgprint(
			msg='Lease Transaction created. Ready for payment. Next transaction on %s.' % (self.next_date),
			title='Lease Transaction Finalized',
			indicator='green')
	
	def create_submit_sales_order(self) -> SalesOrder:
		customer: str = frappe.get_value('Shop', self.leased_to, 'owned_by')
		# payment_terms_template = arst,

		item = frappe.new_doc("Sales Order Item",
					item_code = self.leasing_of,
					delivery_date = self.next_date,
					qty = self.frequency_in_weeks(),
					uom = Room.UOM)

		sales_order: SalesOrder = frappe.new_doc('Sales Order', 
			customer = customer,
			company = self.leased_from,
			transaction_date = self.next_date,
			payment_terms_template = self.frequency_payment_template(),
			items = [ item ],
						# TODO I think I need to manually set the price for this thing?
		)
		return sales_order.submit()

	def create_submit_sales_invoice(self, so: SalesOrder) -> SalesInvoice:
		si: SalesInvoice = make_sales_invoice(so.name)  # needs so.docstatus == 1
		return si.submit()

	def create_save_payment_entry(self, si: SalesInvoice) -> PaymentEntry:
		pe: PaymentEntry = get_payment_entry('Sales Invoice', si.name)  # needs si.docstatus == 1
		return pe.save()

	def create_rent_reminder(self):
		pass

	def save_append_to_transactions(self, so: SalesOrder, si: SalesInvoice, 
								 pe: PaymentEntry = None) -> None:
		self.append('transactions',
			  frappe.new_doc('Lease Transaction',
					sales_order = so, 
					sales_invoice = si, 
					payment_entry = pe,
			  )
		)
		self.save()

	def save_move_next_date(self) -> None:
		def last_period() -> bool:
			return self.next_date > self.end_date
		
		months = self.frequency_in_months()
		# self.set('next_date', frappe.utils.add_months(self.next_date, months))
		self.next_date = frappe.utils.add_months(self.next_date, months)
		# scope when declared; value when evaluated

		# If next_date is after end_date, add a special warning?

		if last_period():
			return
		self.save()
		self.notify_update()


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