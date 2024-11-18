# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
#from frappe.model.document import Document


class AirplaneFlight(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from airplane_mode.airplane_mode.doctype.flight_crew.flight_crew import FlightCrew
		from frappe.types import DF

		airplane: DF.Link
		amended_from: DF.Link | None
		crew_on_flight: DF.TableMultiSelect[FlightCrew]
		date_of_departure: DF.Date
		destination_airport: DF.Link
		destination_airport_code: DF.ReadOnly | None
		duration: DF.Duration
		gate_number: DF.Data
		published: DF.Check
		route: DF.Data | None
		source_airport: DF.Link
		source_airport_code: DF.ReadOnly | None
		status: DF.Literal["Scheduled", "Completed", "Cancelled"]
		time_of_departure: DF.Time
	# end: auto-generated types

	# ==================== 
	# CONTROLLERS
	# ====================

	def before_submit(self):
		self.status = 'Completed'
		pass

	def on_update(self):
		gate_number_changed = self.has_value_changed("gate_number")
		if gate_number_changed:
			self.update_gate_numbers()


	# ==================== 
	# PUBLIC INSTANCE METHODS
	# ====================

	def update_gate_numbers(self):
		# Update associated Tickets.
		self.cascade_value(
			"Airplane Ticket", 
			filters={'flight': self.name}, 
			fields_to_cascade={'gate_number': 'gate_number'}
		)
		# NOTE Ah, I need to modify this so that it can be changed if a Ticket had been submitted.
		# But, for a ticket to be submitted, it needs to be Boarded? So it probably shouldn't be able to be edited after boarding...


	def cascade_value(self, doctype: str, *, filters: dict = None, fields_to_cascade: dict = None):
		"""
		Cascade values from the current object to associated DocType, such as Airplane Tickets.
    
		:param doctype: A string representing the targeted DocType.

		:param filters: A dictionary of filters to put in frappe.get_list. 
				This should include a filter that connects to this Document.

		:param fields_to_cascade: A dictionary where keys are field names in the current object
				and values are the corresponding field names in Airplane Ticket.

		example usage:
		
		self.cascade_value("Airplane Ticket", {'flight': self.name}, {'gate_number': 'gate_number'})
		"""
		items: list[dict] = frappe.get_list(
			doctype, 
			fields=["name"] + list(fields_to_cascade.values()),
			filters=filters
		)

		for item in items:
			updated = False
			for src_field, dst_field in fields_to_cascade.items():

				if getattr(self, src_field) != item[dst_field]:
					doc = frappe.get_cached_doc(doctype, item.name) 
					doc.set(dst_field, getattr(self, src_field))
					updated = True
        
			if updated:
				doc.save()
				doc.notify_update()

	def overcapacity(self) -> bool:
		from airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight import AirplaneFlight
		count = AirplaneFlight.ticket_count(self.name)
		capacity = frappe.db.get_value('Airplane', self.airplane, 'capacity') 
		return count >= capacity

	# ==================== 
	# STATIC METHODS
	# ====================

	@staticmethod
	def ticket_count(flight_name: str) -> int:
		return frappe.db.count('Airplane Ticket', filters={'flight': flight_name})

	@staticmethod
	def overcapacity(flight_name: str):
		from airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight import AirplaneFlight
		count = AirplaneFlight.ticket_count(flight_name)

		airplane = frappe.get_value('Airplane Flight', flight_name)

		capacity = frappe.db.get_value('Airplane', flight.airplane, 'capacity') 
		return count >= capacity
