# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.terms import Case

def execute(filters=None):
	columns_room, rooms = room_count(filters)
	columns_shop, shops = shop_count(filters)
	columns = columns_room + columns_shop

	query = (
		frappe.qb
		.from_(rooms)
		.join(shops)
		.on_field('airport_name')
		.select(
			rooms.star,
			shops.shop_count
		)
	)

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
			'label': 'Available/Reserved Rooms',
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
		  		.else_(None)).as_("available_rooms"),
			Count(Case()
				.when(Room.status == 'Occupied', 1)
				.else_(None)).as_("occupied_rooms"),
			Count(Room.name).as_("total_rooms"),
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
	