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

	# TODO Check if this refactor is suitable
	def cascade_value(self, doctype, filters, fields_to_cascade):
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
		items = frappe.get_list(doctype, 
			fields=["name"] + list(fields_to_cascade.values()),
			filters=filters)

		for item in items:
			updated = False
			for src_field, dst_field in fields_to_cascade.items():

				if getattr(self, src_field) != item[dst_field]:
					doc = frappe.get_doc(doctype, item.name) 
					doc.set(dst_field, getattr(self, src_field))
					updated = True
					# Hmm, is it efficient to use get_doc multiple times?
					# NOTE This seems like premature optimization though.
        
			if updated:
				doc.save()
				doc.notify_update()

	def update_gate_numbers(self):
		self.cascade_value("Airplane Ticket", {'flight': self.name}, {'gate_number': 'gate_number'})
		# NOTE Ah, I need to modify this so that it can be changed if a Ticket had been submitted.
		# But, for a ticket to be submitted, it needs to be Boarded? So it probably shouldn't be able to be edited after boarding...


	def on_submit(self):
		self.status = 'Completed'
		pass

	def on_update(self):
		gate_number_changed = self.has_value_changed("gate_number")
		if gate_number_changed:
			# Update associated Tickets.
			self.update_gate_numbers()