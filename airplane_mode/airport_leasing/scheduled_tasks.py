import frappe
import json

from frappe.query_builder import DocType
# from airplane_mode.airport_leasing.doctype.lease.lease import Lease
# from airplane_mode.airport_leasing.doctype.room.room import default_uom 
# from erpnext.accounts.doctype.payment_entry.payment_entry import ( get_payment_entry, PaymentEntry )
# from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
# from erpnext.selling.doctype.sales_order.sales_order import ( make_sales_invoice, SalesOrder )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF

# "app.scheduled_tasks.update_database_usage"

def send_rent_reminders():
	leases = retrieve_active_leases()
	for lease in leases:
		lease.do_something()
	# Query for all active Leases

def retrieve_active_leases() -> list[str]:
	"""
	select lease.name 
	from tabLease lease
	where lease.docstatus == 1 and lease.end_date < lease.next_date
	finds all active leases with 1 or more period remaining.

	where lease.docstatus == 1 and lease.end_date > lease.next_date
	finds all leases on their last period.
	"""
	lease = DocType('Lease')

	query = ( frappe.qb.from_(lease)
			 .select(lease.name)
			 .where(lease.docstatus.is_submitted())
	)
	frappe.errprint(query.walk())
	return query.run()

def notifications_enabled():
	# Grab Single DocType value

	self.rental_rate = frappe.get_doc('Airport Leasing Settings').run_notifications
	pass


# def on_submit_sales_order(doc: SalesOrder, method=None) -> None:
# 	"""
# 	First trigger on Lease submit, which creates and submits a repeating Sales Order.
# 	Afterwards, triggered AutoRepeat Sales Order
# 	"""
# 	frappe.errprint('Wal: Sales Order submitted, hooking in.')

# 	if not doc.auto_repeat:  # Custom behaviour for initial Sales Order.
# 		pass
	
# 	# NOTE Consider using Async / background jobs?
# 	# frappe.enqueue()
# 	frappe.errprint('Wal: Trying to make Sales Invoice!')

# 	sales_invoice: SalesInvoice = make_sales_invoice(doc.name)
# 	sales_invoice.save()
# 	# sales_invoice.submit()
# 	# This creates and associates a Sales Invoice to this Sales Order.

# 	# payment_entry: PaymentEntry = make_payment_entry()
# 	# payment_entry.save()

# 	# lease.append_transaction(doc.name, sales_invoice.name)


# @frappe.whitelist()
# def force_auto_repeat(doc: str) -> None:
# 	"""
# 	Force a trigger of an AutoRepeat document creation.
# 	Assumes that the AutoRepeat is fully set up.

# 	airplane_mode.airport_leasing.lease_sales_order.force_auto_repeat
# 	"""
# 	sales_order: SalesOrder = frappe.get_doc(json.loads(doc))
# 	auto_repeat = frappe.get_doc('Auto Repeat', sales_order.auto_repeat)
# 	auto_repeat.create_documents()
# 	# auto_repeat.make_new_documents()
# 	pass


# def query_builder(self):
# 	"""
# 	select lease.name, item.item_code as 'Item Code', so.name as 'Sales Order', si.name as 'Sales Invoice'
# 	from `tabSales Invoice` si
# 	left join `tabSales Invoice Item` item
# 	on item.parent = si.name

# 	left join `tabSales Order` so
# 	on item.sales_order = so.name

# 		left join `tabLease` lease
# 		on item.item_code = lease.leasing_of

# 		where so.name = "{self.name}"
# 	"""
# 	sales_invoice = DocType('Sales Invoice')
# 	item = DocType('Sales Invoice Item')
# 	sales_order = DocType('Sales Order')
# 	lease = DocType('Lease')

# 	query = (
# 		frappe.qb.from_(sales_invoice)
# 			.inner_join(item).on(item.parent == sales_invoice.name)
# 			.inner_join(sales_order).on(sales_order.name == item.sales_order)
# 			.inner_join(lease).on(item.item_code == lease.leasing_of)
# 			.where(sales_order.name == self.name)
# 			.select(
# 				  sales_order.name,
# 				  sales_invoice.name, 
# 				  item.item_code, 
# 				  sales_order.created_on
# 			)
# 			.distinct()
# 	)
# 	return query.run()
