# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

from erpnext.selling.doctype.sales_order.sales_order import SalesOrder 
from frappe.automation.doctype.auto_repeat.auto_repeat import AutoRepeat
from airplane_mode.airport_leasing.doctype.room.room import default_uom 

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF
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
		start_date: DF.Date
		transactions: DF.Table[LeaseTransaction]
	# end: auto-generated types
	pass

	def on_submit(self) -> None:
		self.create_submit_repeating_sales_order()


	def create_submit_repeating_sales_order(self) -> None:
		sales_order: SalesOrder = create_sales_order(self)
		auto_repeat: AutoRepeat = create_auto_repeat('Sales Order', sales_order.name, 
				   self.start_date, self.end_date, self.invoice_frequency)
		sales_order.submit()  
		# on_submit, sales_order creates sales invoice then adds to Lease.transactions

		frappe.msgprint(
			msg='Sales Order "%s" created, submitted, and scheduled for auto-repeat.' % (sales_order.name),
			title='Sales Order Finalized',
			indicator='green')
	
	
	def append_transaction(self, sales_order: str, sales_invoice: str) -> None:
		self.append('transactions',
			transaction := frappe.new_doc('Lease Transaction', 
				sales_order = sales_order.name, 
				sales_invoice = sales_invoice.name
				)
		)
		self.save()

	
	@frappe.whitelist()
	def return_owo(self):
		return f"OwO {self.name}"

	@staticmethod
	def select_frequency(choice: str, uom: str='Week') -> int:
		weeks = {'Monthly': 4, 'Quarterly': 12}
		uoms = {'Week': 1, 'Month': 4}

		numerator = weeks.get(choice, 0)
		divisor = uoms.get(uom, 1)
		return int(numerator / divisor)


# NOTE This involves working with Item child table UOMConversionDetail
def item_uom() -> str:
	return default_uom()  # from `room.py`


def create_sales_order(lease: Lease) -> SalesOrder:
	customer: str = frappe.get_value('Shop', lease.leased_to, 'owned_by')
	uom = item_uom()
	item_weeks: int = Lease.select_frequency(lease.invoice_frequency, uom)

	sales_order: SalesOrder = frappe.new_doc('Sales Order', 
		customer = customer,
		company = lease.leased_from,
		items = [ 
			frappe.new_doc("Sales Order Item",
			item_code = lease.leasing_of,
			delivery_date = lease.start_date,
			qty = item_weeks,
			uom = uom,
			)
		])
	sales_order.insert()
	return sales_order


def create_auto_repeat(doctype, docname, frequency, start_date, end_date) -> AutoRepeat:
	doc = frappe.new_doc("Auto Repeat",
		reference_doctype = doctype,
		reference_document = docname,
		frequency = frequency,
		start_date = start_date,
		end_date = end_date,
		submit_on_creation = 1
		)
	doc.insert()
	return doc
