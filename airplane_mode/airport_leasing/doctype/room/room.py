# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


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

	# def create_related_item_entry(self):
	# 	airport_code = frappe.db.get_value('Airport', self.airport, 'code')
	# 	rental_rate = frappe.db.get_single_value('Airport Leasing Settings', 'default_rental_rate') 
		
	# 	item = frappe.new_doc( 'Item', 
	# 		item_code = f'{airport_code}{self.room_number}',
	# 		item_group = 'Real Estate Leasing',
	# 		stock_uom = 'Week',
	# 		is_stock_item = 0,
	# 		is_purchase_item = 0,
	# 		grant_commission = 0,
	# 		sales_uom = 'Week',
	# 		include_item_in_manufacturing = 0,
	# 		standard_rate = rental_rate
	# 	)
	# 	# TODO Should I add Item Tax Template fields as well?

	# 	# TODO Set the below if this room is somehow not for use.
	# 	# is_sales_item = 0,

	# 	item.insert()
	# 	return item

	def autoname(self):
		self.name = f"{frappe.db.get_value('Airport', self.airport, 'code')}{self.room_number}"


# TODO Fix the fragility of this function with try / except.
@frappe.whitelist()
def create_item(doc: str):
	"""
	Creates a related Item entry for the Room.

	This method generates a new Item document with the following details:
	- Item code: Combination of airport code and room number
	- Item group: 'Real Estate Leasing'
	- Stock UOM: 'Week'
	- Sales UOM: 'Week'
	- Is stock item: False
	- Is purchase item: False
	- Grant commission: False
	- Include item in manufacturing: False
	- Standard rate: Default rental rate from Airport Leasing Settings

	Returns:
		frappe.Document: The newly created Item document
	"""
	doc_dict = json.loads(doc)

	airport_code = frappe.db.get_value('Airport', doc_dict['airport'], 'code')
	rental_rate = frappe.get_doc('Airport Leasing Settings').default_rental_rate

	item = frappe.new_doc('Item', 
		item_code = f"{airport_code}{doc_dict['room_number']}",
		item_group = 'Real Estate Leasing',
		stock_uom = 'Week',
		is_stock_item = 0,
		is_purchase_item = 0,
		grant_commission = 0,
		sales_uom = 'Week',
		include_item_in_manufacturing = 0,
		standard_rate = rental_rate
	)

	item.insert()

	frappe.msgprint(
		msg='Item "%s" created and associated to this Room.' % (item.name),
		title='Room Item Creation',
		indicator='green')
	pass