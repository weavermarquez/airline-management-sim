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
		entrances_and_exits: DF.Int
		height: DF.Float
		length: DF.Float
		operated_by: DF.Link | None
		rental_rate: DF.Currency
		rental_rate_override: DF.Currency
		room_number: DF.Int
		status: DF.Literal["Vacant", "Leased", "Under maintenance"]
		width: DF.Float
	# end: auto-generated types
	pass

	UOM = 'Week'
	ITEM_GROUP = 'Real Estate Leasing'

	# ==================== 
	# CONTROLLERS 
	# ====================

	def autoname(self) -> None:
		airport_code = frappe.get_value('Airport', self.airport, 'code')
		self.name = f"{airport_code}{self.room_number}"


	def on_submit(self) -> None:
		if not self.item_exists():
			self.create_item()

	def on_update_after_submit(self) -> None:
		# read only:
		# item next date
		# transactions
		pass

	@property
	def rental_rate(self) -> float:
		return frappe.get_doc('Airport Leasing Settings').default_rental_rate

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	def item_exists(self) -> bool:
		return frappe.db.exists('Item', self.name)

	def auto_rental_rate(self) -> float:
		"""Order of selecting rental rates
		1. User-set document rate in Room
		2. User-set global rate in Airport Leasing Settings
		3. App-set global rate in Airport Leasing Settings"""

		if self.rental_rate_override:
			return self.rental_rate_override
		else:
			return self.rental_rate

	def create_item(self) -> None:
		item: Item = frappe.new_doc('Item', 
			item_code = self.name,
			item_group = Room.ITEM_GROUP,
			stock_uom = Room.UOM,
			sales_uom = Room.UOM,
			standard_rate = self.auto_rental_rate(),
			is_stock_item = 0,
			is_purchase_item = 0,
			grant_commission = 0,
			include_item_in_manufacturing = 0,
		)
		item.save()
		self.notify_update()
		frappe.msgprint(
			msg='Item "%s" created and associated to this Room.' % (self.name),
			title='Room Item Creation',
			indicator='green')

	# Not happy with this. TODO solve with Domain Driven Design.
	def available(self) -> bool:
		"""Room must be Vacant before adding to new Leases"""
		from typing_extensions import assert_never
		match self.status:
			case 'Vacant':
				return True
			case 'Under maintenance' | 'Leased':
				return False
			case _:
				assert_never(self.status)
	
# TODO Fix the fragility of this function with try / except.
@frappe.whitelist()
def create_item(doc: str) -> None:
	room: Room = frappe.get_doc(json.loads(doc))
	if not room.item_exists():
		room.create_item()
