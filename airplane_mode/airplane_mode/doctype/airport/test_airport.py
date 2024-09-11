# Copyright (c) 2024, Weaver Marquez and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAirport(FrappeTestCase):
	def setUp(self):
		self.airport = frappe.new_doc('Airport',
			name = 'Manitobah Airport',
			city = 'Manitobah',
			country = 'Canada',
			code = 'MBH')

	def test_uwu(self):
		self.assertEquals(self.airport.uwu(), "uwu")
