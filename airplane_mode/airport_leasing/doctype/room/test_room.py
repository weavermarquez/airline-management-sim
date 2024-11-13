# Copyright (c) 2024, Weaver Marquez and Contributors
# See license.txt

import frappe
from contextlib import contextmanager
from frappe.tests.utils import FrappeTestCase
from unittest.mock import ( MagicMock, Mock, patch )
from airplane_mode.airport_leasing.doctype.room.room import Room

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.types import DF
	from erpnext.stock.doctype.item.item import Item
	from airplane_mode.airplane_mode.doctype.airport.airport import Airport


class TestRoomUnit(FrappeTestCase):
	"""Unit Tests for Room. 
	Focuses on mocking static and public instance methods with mocks."""

	# ===============================
	# FIXTURES
	# ===============================

	@classmethod
	def setUpClass(cls):
		"""Runs once before all test in the class"""
		super().setUpClass()

		# Create shared test data that won't be modified by tests
		cls.common_data = {
			'airport': 'TEST_AIRPORT',
			'airport_code': 'TEST_AIRPORT',
			'room_number': 101,
			'maintenance': False
		}

	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		# Clean up any class-level resources.

	def setUp(self):
		"""Run before each test method"""
		self.room = frappe.new_doc('Room', **self.common_data)

	@contextmanager
	def mock_frappe_calls(self):
		"""Fixture that mocks common Frappe calls"""
		with patch('frappe.get_value') as mock_get_value, \
			patch('frappe.get_all') as mock_get_all, \
			patch('frappe.new_doc') as mock_new_doc:
			
			mock_get_value.return_value = 'TEST'
			yield {
				'get_value': mock_get_value,
				'get_all': mock_get_all,
				'new_doc': mock_new_doc
			}

	@staticmethod
	def status_cases():
		DRAFT = 0
		SUBMITTED = 1
		CANCELLED = 2
		return [
			{
				"expected_status": "Available",
				"docstatus" : SUBMITTED,
				"maintenance": False,
				"draft_leases": [],
				"active_leases": []
			},
			{
				"expected_status": "Occupied",
				"docstatus" : SUBMITTED,
				"maintenance": False,
				"draft_leases": [],
				"active_leases": [{"name": "ACTIVE1"}]
			},
			{
				"expected_status": "Occupied",
				"docstatus" : SUBMITTED,
				"maintenance": False,
				"draft_leases": [{"name": "DRAFT1"}],
				"active_leases": [{"name": "ACTIVE1"}]
			},
			{
				"expected_status": "Reserved",
				"docstatus" : SUBMITTED,
				"maintenance": False,
				"draft_leases": [{"name": "DRAFT1"}],
				"active_leases": []
			},
			{
				"expected_status": "Maintenance",
				"docstatus" : SUBMITTED,
				"maintenance": True,
				"draft_leases": [],
				"active_leases": []
			},
			{
				"expected_status": "Maintenance",
				"docstatus" : SUBMITTED,
				"maintenance": True,
				"draft_leases": [{"name": "DRAFT1"}],
				"active_leases": [{"name": "ACTIVE1"}]
			},
			{
				"expected_status": "Cancelled",
				"docstatus": CANCELLED,
				"maintenance": True,
				"draft_leases": [{"name": "DRAFT1"}],
				"active_leases": [{"name": "ACTIVE1"}]
			},
			{
				"expected_status": "Draft",
				"docstatus": DRAFT,
				"maintenance": True,
				"draft_leases": [{"name": "DRAFT1"}],
				"active_leases": [{"name": "ACTIVE1"}]
			},
		]


	@classmethod
	def _add_test(cls, case_number, case):
		def mock_get_all(doctype, filters=None):
			docstatus = filters.get('docstatus')[1]
			draft_active_leases = {
				0: case['draft_leases'], 
				1: case['active_leases']
			}
			return draft_active_leases.get(docstatus[0], [])

		@patch('frappe.get_all', mock_get_all)
		def test_method(self):
			self.room.maintenance = case['maintenance']
			self.room.docstatus = case['docstatus']
			self.room.set_status(update=False)

			self.assertEqual(
				self.room.status, 
				case['expected_status'],
				f"Failed for case: {case}"
			)

		setattr(cls, f'test_set_status_{case_number}', test_method)
		test_method.__name__ = f'test_set_status_{case_number}'

	@classmethod
	def make_comprehensive_status_tests(cls):
		test_cases = TestRoomUnit.status_cases()
		for case_number, case in enumerate(test_cases):
			cls._add_test(case_number, case)


	# def test_set_status_comprehensive(self):
	# 	for index, case in enumerate(TestRoomUnit.status_cases()):
	# 		with self.subTest(f"set_status subtest {index}", index=index, case=case):
	# 			self.assertRequal
	# 			self.test_two
	# 	pass


	# ===============================
	# CONTROLLERS
	# ===============================

	def test_autoname_with_get_value(self):
		"""Assumes that room calls frappe.get_value()."""
		expected_room_name = f"{self.common_data['airport_code']}{self.common_data['room_number']}"

		with patch('frappe.get_value', return_value=self.common_data['airport_code']) as mock_get_value:
			self.room.autoname()
			with self.subtest("Autoname should use frappe.get_value()"):
				mock_get_value.assert_called_once_with('Airport', self.room.airport, 'code')

			with self.subtest("The result of autoname should follow {airport_code}{room_number}"):
				self.assertEqual(self.room.name, expected_room_name)


	# item_exists
	def test_auto_rental_rate(self):
		self.fail("Not Implemented")

	# ===============================
	# PUBLIC INSTANCE METHODS
	# ===============================

	def test_something(self):
		with self.mock_frappe_calls() as mocks:
			# Use the mocked functions
			self.room.autoname()
			mocks['get_value'].assert_called_once()

	def test_create_item_called(self):
		mock_item = Mock()
		with patch('frappe.new_doc', return_value=mock_item) as mock_new_doc:
			self.room.create_item()

			with self.subtest("Item is created"):
				mock_new_doc.assert_called_once()

			with self.subtest("Item is saved to DB"):
				mock_item.save.assert_called_once()

	def test_on_submit(self):
		"""A Unit Test-like approach that 
		Patch both the instance method and the link validation.
		An integration approach may be preferrable.
		"""

		with patch.object(Room, 'create_item') as mock_create_item, \
			 patch('frappe.get_doc') as mock_get_doc:
			# Setup mock airport for link validation
			mock_airport = Mock()
			mock_airport.name = 'TEST_AIRPORT'
			mock_get_doc.return_value = mock_airport
			
			with patch.object(Room, 'item_exists', return_value=False):
				self.room.on_submit()
				mock_create_item.assert_called_once()

TestRoomUnit.make_comprehensive_status_tests()


class TestRoomIntegration(FrappeTestCase):
	"""Integration Tests for Room.
	Focus on using real documents."""
	# ===============================
	# FIXTURES
	# ===============================

	@classmethod
	def setUpClass(cls):
		"""Runs once before all test in the class"""
		super().setUpClass()

		# Create shared test data that won't be modified by tests
		cls.airport_data = {
			'name': '_Test Airport',
			'code': 'TST',
			'country': 'TEST COUNTRY',
			'city': 'TEST CITY'
		}
		cls.room_data = {
			'airport': cls.airport_data['name'],
			'room_number': 101,
			'maintenance': False
		}

	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		# Clean up any class-level resources.

	def setUp(self):
		"""Run before each test method"""
		self.airport = frappe.new_doc('Airport', **self.airport_data).insert()
		self.room = frappe.new_doc('Room', **self.room_data)

	def tearDown(self):
		self.airport.delete()

	# ===============================
	# CONTROLLERS
	# ===============================

	# Autoname
	# Validate
	# On Submit
	# On Update After Submit
	# Rental Rate

	def test_autoname(self):
		self.fail("Not Implemented")

	def test_validate(self):
		self.fail("Not Implemented")

	def test_on_submit(self):
		self.fail("Not Implemented")

	def test_on_update_after_submit(self):
		self.fail("Not Implemented")

	def test_rental_rate(self):
		self.fail("Not Implemented")

	# ===============================
	# PUBLIC INSTANCE METHODS
	# ===============================

	# Auto Rental Rate
	# Item Exists
	# Create Item
	# Set Status

	def test_auto_rental_rate(self):
		self.fail("Not Implemented")

	def test_item_exists(self):
		self.fail("Not Implemented")

	def test_create_item(self):
		self.fail("Not Implemented")

	def test_set_status(self):
		self.fail("Not Implemented")

