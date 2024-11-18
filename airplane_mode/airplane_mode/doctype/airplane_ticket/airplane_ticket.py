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

	# ==================== 
	# CONTROLLERS
	# ====================
	
	def onload(self):
		self.validate_gate_number()

	def before_insert(self):
		self.validate_flight_capacity()
		self.assign_random_seat()

	def validate(self):
		self.remove_duplicate_add_ons()
		self.total_amount = self.total_price()

	def before_submit(self):
		self.validate_value('status', '!=', 'Boarded')

	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	def assign_random_seat(self) -> None:
		seat_row, seat_col = AirplaneTicket.random_seat()
		self.seat = f"{seat_row}{seat_col}"

	def validate_flight_capacity(self) -> None:
		flight = frappe.get_doc('Airplane Flight', self.flight)
		if flight.overcapacity():
			frappe.throw("Capacity for Airplane Flight has been exceeded.")

	# TODO Should I remove this now that changes to Flight's gate_number cascade to Tickets?
	# Because it seems like a better option than otherwise...
	def validate_gate_number(self) -> None:
		if self.gate_number:
			expected_gate_number = frappe.get_value('Airplane Flight', self.flight, 'gate_number')
			self.validate_value('gate_number', '=', expected_gate_number, raise_exception=True)

	def remove_duplicate_add_ons(self) -> None:
		"""Remove duplicate add_ons based on add_on.id"""
		duplicates, uniques = AirplaneTicket.find_duplicates_by_key(self.add_ons, "item")
		for d in duplicates:
			self.add_ons.remove(d)

	def total_price(self) -> float:
		return self.flight_price + sum([item.amount for item in self.add_ons])	
		
	# ==================== 
	# STATIC METHODS
	# ====================

	@staticmethod
	def find_duplicates_by_key(lst, key) -> tuple[dict, dict]:
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
	def random_seat() -> tuple[int, str]:
		seat_row = random.randint(1, 100)
		# Generate a random capital letter from A to E
		seat_col = random.choice(string.ascii_uppercase[:5])
		return seat_row, seat_col
