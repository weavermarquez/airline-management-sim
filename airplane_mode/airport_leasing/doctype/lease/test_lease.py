# Copyright (c) 2024, Weaver Marquez and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
# from airplane_mode.airport_leasing.doctype.lease.lease import Lease
# from unittest.mock import patch, MagicMock

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
# 	from frappe.types import DF
# 	from erpnext.selling.doctype.customer.customer import Customer
# 	from frappe.model.document import Document

class TestLease(FrappeTestCase):
	def test_the_shit(self):
		self.assertEqual(1,1)
	# def setUp(self):
	# 	# Create test data
	# 	self.lease = frappe.new_doc( 'Lease', **{
	# 		"leasing_of": "TEST-ROOM-001",
	# 		"leased_to": "TEST-SHOP-001",
	# 		"leased_from": "TEST-COMPANY-001",
	# 		"start_date": "2024-01-01",
	# 		"end_date": "2024-12-31",
	# 		"invoice_frequency": "Monthly",
	# 		"rental_rate": 1000
	# 	})
	# 	self.lease.insert()

	# def tearDown(self):
	# 	frappe.delete_doc("Lease", self.lease.name)


	# def test_select_frequency(self):
	# 	units_per_period = Lease.select_frequency('Monthly','Week')
	# 	self.assertEqual(units_per_period, 4)

	# 	units_per_period = Lease.select_frequency('Quarterly','Month')
	# 	self.assertEqual(units_per_period, 3)

	# # TODO Test for multiple dates in relation to Item creation date
	# def test_item_created_with_default_rate(self):
	# 	default_rate = 5000
	# 	settings = frappe.get_doc('Airport Leasing Settings')
	# 	settings.default_rental_rate = default_rate
	# 	settings.save()

	# 	# self.room.submit()
	# 	self.room.on_submit()
	# 	# Check that item exists
	# 	item_code = self.room.room_name()
	# 	item_exists = frappe.db.exists('Item', item_code)
	# 	if not item_exists:
	# 		self.fail('Item does not exist')
	# 	self.assertEqual(frappe.get_doc('Item', item_code).standard_rate, default_rate)


	# @patch('frappe.get_value')
	# @patch.object(Lease, 'create_submit_sales_order')
	# @patch.object(Lease, 'create_submit_sales_invoice')
	# @patch.object(Lease, 'save_append_to_transactions')
	# @patch.object(Lease, 'save_move_next_date')
	# def test_create_lease_transaction(self, mock_save_move_next_date, mock_save_append_to_transactions, 
	# 								  mock_create_submit_sales_invoice, mock_create_submit_sales_order, 
	# 								  mock_get_value):
	# 	# Mock frappe.get_value for Shop's owned_by
	# 	mock_get_value.return_value = "TEST-CUSTOMER-001"

	# 	# Mock Sales Order
	# 	mock_so = MagicMock()
	# 	mock_so.name = "SO-001"
	# 	mock_create_submit_sales_order.return_value = mock_so

	# 	# Mock Sales Invoice
	# 	mock_si = MagicMock()
	# 	mock_si.name = "SI-001"
	# 	mock_create_submit_sales_invoice.return_value = mock_si

	# 	# Call the method to test
	# 	self.lease.create_lease_transaction()

	# 	# Assertions
	# 	mock_get_value.assert_called_once_with('Shop', 'TEST-SHOP-001', 'owned_by')
	# 	mock_create_submit_sales_order.assert_called_once()
	# 	mock_create_submit_sales_invoice.assert_called_once_with(mock_so)
	# 	mock_save_append_to_transactions.assert_called_once_with(mock_so, mock_si, None)
	# 	mock_save_move_next_date.assert_called_once()

	# Add individual tests for create_submit_sales_order, create_submit_sales_invoice, etc.
	# def test_create_submit_sales_order(self):
	# 	self
	# 	# Test implementation for create_submit_sales_order
	# 	pass

	# def test_create_submit_sales_invoice(self):
	# 	# Test implementation for create_submit_sales_invoice
	# 	pass

	# ... other individual component tests ...