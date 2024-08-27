# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Room(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.Link | None
		airport: DF.Link
		airport_code: DF.ReadOnly | None
		area: DF.Int
		capacity: DF.Int
		item: DF.Link | None
		operated_by: DF.Link | None
		room_number: DF.Int
	# end: auto-generated types
	pass

	# NOTE This should no longer be necessary.
	def create_related_location_entry(self):
		airport_code = frappe.db.get_value('Airport', self.airport, 'code')
		#airport_location = frappe.get_doc('Location', self.airport)

		location = frappe.new_doc( 'Location', 
			location_name = f'{airport_code}{self.room_number}',
			parent_location = self.airport,
			# TODO Create a fixture for Airport Location?
		)

		location.insert()
		return location
		

	# NOTE This should no longer be necessary if Rooms are not listed as Assets.
	def create_related_asset_entry(self):
		airport_code = frappe.db.get_value('Airport', self.airport, 'code')
		room_location = self.create_related_location_entry()

		company = frappe.db.get_value('Lease', self.airport, 'leased_from')

		companies = frappe.get_list('Lease', 
							  fields=['name', 'leased_from'], 
							  filters={'leasing_of': self.name, 'docstatus': 1})
							  # Add list-form filters for checking Dates of the Lease

		if len(companies) == 0:
			frappe.throw("This Room has no valid Leases")
			# TODO Wait, what? Why does this need a valid Lease?
		
		asset = frappe.new_doc( 'Asset', 
			company = companies[0].leased_from,
			item_code = f'{airport_code}{self.room_number}',
			asset_name = f'{airport_code}{self.room_number}',
			location = room_location.name,
			is_existing_asset = 1,
			available_for_use_date = frappe.utils.today() , #today
			gross_purchase_amount = 0,
			asset_category = 'Airport Room'
			# TODO Add Item Tax Template
		)

		asset.insert()
		return asset

	def create_related_item_entry(self):
		airport_code = frappe.db.get_value('Airport', self.airport, 'code')
		
		item = frappe.new_doc( 'Item', 
			item_code = f'{airport_code}{self.room_number}',
			item_group = 'Real Estate Leasing',
			stock_uom = 'Week',
			is_stock_item = 0,
			is_purchase_item = 0,
			grant_commission = 0,
			sales_uom = 'Week',
			include_item_in_manufacturing = 0

			#is_fixed_asset = 1,
			#asset_category = 'Airport Room'
			# TODO Add Item Tax Template
		)

		item.insert()
		return item

	def before_insert(self):
		item = self.create_related_item_entry()
		self.item = item.name
		return True
