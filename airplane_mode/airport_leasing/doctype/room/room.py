# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF
	from erpnext.stock.doctype.item.item import Item

class Room(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		airport: DF.Link
		amended_from: DF.Link | None
		area: DF.Int
		capacity: DF.Int
		operated_by: DF.Link | None
		room_number: DF.Int
		status: DF.Literal["Vacant", "Leased", "Under maintenance"]
	# end: auto-generated types
	pass

	def on_submit(self):
		_create_item(self)

	def autoname(self):
		self.name = self.room_name()

	def room_name(self):
		airport_code = frappe.get_value('Airport', self.airport, 'code')
		return f"{airport_code}{self.room_number}"


@frappe.whitelist()
def default_uom() -> str:
	uom: str = frappe.db.get_single_value('Airport Leasing Settings', 'default_uom')
	if not uom:
		uom = 'Week'
	return uom


# TODO Fix the fragility of this function with try / except.
@frappe.whitelist()
def create_item(doc: str) -> None:
	room: Room = frappe.get_doc(json.loads(doc))
	return _create_item(room)

def _create_item(room: Room) -> None:
	rental_rate: int = frappe.get_doc('Airport Leasing Settings').default_rental_rate
	# I need to use get_doc because get_single_value doesn't retrieve defaults.
	item_code = room.room_name()
	uom = default_uom()

	item_group = 'Real Estate Leasing'
	# TODO I should really add a field to the Airport Leasing Setttings about Units of Measurement.

	item: Item = frappe.new_doc('Item', 
		item_code = item_code,
		item_group = item_group,
		stock_uom = uom,
		sales_uom = uom,
		standard_rate = rental_rate,
		is_stock_item = 0,
		is_purchase_item = 0,
		grant_commission = 0,
		include_item_in_manufacturing = 0,
	)

	item.insert()

	frappe.msgprint(
		msg='Item "%s" created and associated to this Room.' % (item_code),
		title='Room Item Creation',
		indicator='green')