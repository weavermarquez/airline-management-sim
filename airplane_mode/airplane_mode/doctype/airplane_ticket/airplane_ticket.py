# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random
import string

class AirplaneTicket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from airplane_mode.airplane_mode.doctype.airplane_ticket_add_on_item.airplane_ticket_add_on_item import AirplaneTicketAddonItem
		from frappe.types import DF

		add_ons: DF.Table[AirplaneTicketAddonItem]
		amended_from: DF.Link | None
		departure_date: DF.Date | None
		departure_time: DF.Time | None
		destination_airport_code: DF.ReadOnly | None
		duration_of_flight: DF.Duration | None
		flight: DF.Link
		flight_price: DF.Currency
		gate_number: DF.ReadOnly | None
		passenger: DF.Link
		seat: DF.Data | None
		source_airport_code: DF.ReadOnly | None
		status: DF.Literal["Booked", "Checked-In", "Boarded"]
		total_amount: DF.Currency
	# end: auto-generated types

	@staticmethod
	def find_duplicates_by_key(lst, key):
		"""Returns the duplicate and unique list of dictionaries based on a single key comparison."""
		seen = set()
		uniques = []
		duplicates = []
		for d in lst:
			# t = tuple(d.as_dict()[key] for key in keys if key in d.as_dict())
			# If the tuple is in the seen set, it's a duplicate
			t = d.as_dict()[key]
			if t in seen:
				duplicates.append(d)
			else:
				uniques.append(d)
				seen.add(t)
		return duplicates, uniques

	@staticmethod
	def random_seat():
		seat_row = random.randint(1, 100)
		# Generate a random capital letter from A to E
		seat_col = random.choice(string.ascii_uppercase[:5])
		return seat_row, seat_col

	# TODO Should I remove this now that changes to Flight's gate_number cascade to Tickets?
	# Because it seems like a better option than otherwise...
	def check_gate_number(self):
		# x = count of tickets linked to self.flight
		flight = frappe.get_doc('Airplane Flight', self.flight)
		if (flight.gate_number and flight.gate_number != self.gate_number):
			frappe.throw("Flight's Gate != Ticket Gate")
		    #self.gate_number = flight.gate_number

	def overcapacity(self):
		# x = count of tickets linked to self.flight
		count = frappe.db.count('Airplane Ticket', {'flight': self.flight} )
		# y = self.flight.airplane.capacity
		flight = frappe.get_doc('Airplane Flight', self.flight)
		capacity = frappe.db.get_value('Airplane', flight.airplane, 'capacity') 
		return count >= capacity

	def before_insert(self):
		seat_row, seat_col = AirplaneTicket.random_seat()
		self.seat = f"{seat_row}{seat_col}"
		if self.overcapacity():
			frappe.throw("Capacity for Airplane Flight has been exceeded.")

	def validate(self):
		# Find duplicates based on 'id'
		duplicates, uniques = AirplaneTicket.find_duplicates_by_key(self.add_ons, "item")
		for d in duplicates:
			self.add_ons.remove(d)

		self.total_amount = self.flight_price + sum([d.amount for d in uniques])	
		# self.add_ons = 

		return True

	def before_submit(self):
		if self.status != 'Boarded':
			frappe.throw("Status must be Boarded to submit Ticket")
		