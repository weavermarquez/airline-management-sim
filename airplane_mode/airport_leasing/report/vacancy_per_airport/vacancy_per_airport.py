# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.terms import Case

def execute(filters=None):
	col_a, rooms = room_count(filters)
	col_b, shops = shop_count(filters)
	columns = col_a + col_b

	query = (
		frappe.qb
		.from_(rooms)
		.join(shops)
		.on_field('airport_name')
		# .on(rooms.airport_name == shops.airport_name)
		.select(
			rooms.star,
			shops.shop_count
		)
	)

	# DONE Find a way to avoid having to bring in a Pypika Table.
	# Attempting to use .on(rooms.airport_name == shops.airport_name) 
	# or .on_field('airport_name') did not work.
	# https://github.com/kayak/pypika/issues/755

	# Turns out it just needs to be through frappe.qb rather than one of the preexisting queries.

	# Airport = DocType("Airport")
	# query = (
	# 	rooms
	# 	.join(shops)
	# 	# .on(Airport.name == shops.airport_name)
	# 	.on(rooms.airport_name == shops.airport_name)
	# 	.select(
	# 		shops.shop_count,
	# 	)
	# )

	frappe.log(query.walk())
	results = query.run()

	return columns, results

def room_count(filters=None):
	columns = [
		{
			'fieldname': 'airport_name',
			'label': 'Airport',
			'fieldtype': 'Link',
			'options': 'Airport'
		},
		{
			'fieldname': 'available_rooms',
			'label': 'Available Rooms',
			'fieldtype': 'Int',
		},
		{
			'fieldname': 'occupied_rooms',
			'label': 'Occupied Rooms',
			'fieldtype': 'Int',
		},
		{
			'fieldname': 'total_rooms',
			'label': 'Total Rooms',
			'fieldtype': 'Int',
		},
	]

	Room = DocType("Room")
	Airport = DocType("Airport")

	query = (
		frappe.qb
		.from_(Room)
		.join(Airport)
		.on(Room.airport == Airport.name)
		.select(
			Airport.name.as_("airport_name"),
			Count(Case()
				.when((Room.status == 'Available') | (Room.status == 'Reserved'), 1)
		  		.else_(None)).as_("Available/Reserved Rooms"),
			Count(Case()
				.when(Room.status == 'Occupied', 1)
				.else_(None)).as_("Occupied Rooms"),
			Count(Room.name).as_("Total Rooms"),
		)
		.where(Room.docstatus==1)
		.groupby(Airport.name)
	)

	return columns, query

def shop_count(filters=None):
	columns = [
		{
			'fieldname': 'shop_count',
			'label': 'Shop Count',
			'fieldtype': 'Int',
		}
	]

	Room = DocType("Room")
	Lease = DocType("Lease")

	query = (
		frappe.qb
		.from_(Lease)
		.join(Room)
		.on(Lease.leasing_of == Room.name)
		.select(
			Room.airport.as_("airport_name"),
			Count(Lease.leased_to).as_("shop_count"),
		)
		.where(Lease.docstatus==1)
		.groupby(Room.airport)
	)
	return columns, query
	