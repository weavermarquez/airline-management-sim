import frappe
import json

from erpnext.selling.doctype.sales_order.sales_order import ( make_sales_invoice, SalesOrder )
from airplane_mode.airport_leasing.doctype.lease.lease import Lease

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
    from frappe.types import DF


def on_submit_sales_order(doc: SalesOrder, method=None) -> None:
    """
    First trigger on Lease submit, which creates and submits a repeating Sales Order.
    Afterwards, triggered AutoRepeat Sales Order
    """
    if not (lease := relevant_lease(doc)):
        return

    if not doc.auto_repeat:  # Custom behaviour for initial Sales Order.
        pass
    
    # NOTE Consider using Async / background jobs?
    # frappe.enqueue()

    sales_invoice: SalesInvoice = make_sales_invoice(doc.name)
    sales_invoice.save()
    # This creates and associates a Sales Invoice to this Sales Order.

    lease.append_transaction(doc.name, sales_invoice.name)


def relevant_lease(doc: SalesOrder) -> None | Lease:
    if not (children := doc.get_all_children()):
        return

    item_code: str = children[0].item_code

    lease_list = frappe.get_list('Lease', fields=['name'],
        filters={'leasing_of':item_code, 'docstatus':'1'},
        order_by='modified desc')
    if not lease_list:
        return

    lease = frappe.get_doc('Lease',lease_list[0])
    return lease


@frappe.whitelist()
def force_auto_repeat(doc: str) -> None:
    """
    Force a trigger of an AutoRepeat document creation.
    Assumes that the AutoRepeat is fully set up.

    airplane_mode.airport_leasing.lease_sales_order.force_auto_repeat
    """
    sales_order: SalesOrder = frappe.get_doc(json.loads(doc))
    auto_repeat = frappe.get_doc('Auto Repeat', sales_order.auto_repeat)
    auto_repeat.create_documents()
    # auto_repeat.make_new_documents()
    pass


@frappe.whitelist()
def default_uom() -> str:
	uom: str = frappe.db.get_single_value('Airport Leasing Settings', 'default_uom')
	if not uom:
		uom = 'Week'
	return uom


# def query_builder(self):
#     """
#     select lease.name, item.item_code as 'Item Code', so.name as 'Sales Order', si.name as 'Sales Invoice'
#     from `tabSales Invoice` si
#     left join `tabSales Invoice Item` item
#     on item.parent = si.name

#     left join `tabSales Order` so
#     on item.sales_order = so.name

#         left join `tabLease` lease
#         on item.item_code = lease.leasing_of

#         where so.name = "{self.name}"
#     """
#     sales_invoice = DocType('Sales Invoice')
#     item = DocType('Sales Invoice Item')
#     sales_order = DocType('Sales Order')
#     lease = DocType('Lease')

#     query = (
#         frappe.qb.from_(sales_invoice)
#             .inner_join(item).on(item.parent == sales_invoice.name)
#             .inner_join(sales_order).on(sales_order.name == item.sales_order)
#             .inner_join(lease).on(item.item_code == lease.leasing_of)
#             .where(sales_order.name == self.name)
#             .select(
#                   sales_order.name,
#                   sales_invoice.name, 
#                   item.item_code, 
#                   sales_order.created_on
#             )
#             .distinct()
#     )
#     return query.run()
