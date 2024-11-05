# Copyright (c) 2024, Weaver Marquez and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from airplane_mode.airport_leasing.doctype.lease.lease import Lease
from unittest.mock import (MagicMock, Mock, patch, call)

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
# 	from frappe.types import DF
# 	from erpnext.selling.doctype.customer.customer import Customer
# 	from frappe.model.document import Document

class TestLeaseUnit(FrappeTestCase):
	"""Unit Tests for Lease. 
	Focuses on mocking static and public instance methods with mocks."""

	# ===============================
	# FIXTURES
	# ===============================

	@classmethod
	def setUpClass(cls):
		"""Runs once before all test in the class"""
		super().setUpClass()
		cls.common_data = {
			'name': '_Test Lease',
			'leasing_of': 'TEST_ROOM',
			'leased_from': 'TEST_COMPANY',
			'leased_to': 'TEST_CUSTOMER',
			'start_date': frappe.utils.today(),
			'end_date': frappe.utils.add_to_date(frappe.utils.today(), months=6),
			'period_length': 'Monthly',
		}

	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		# Clean up any class-level resources.

	def setUp(self):
		"""Run before each test method"""
		self.lease = frappe.new_doc('Lease', **self.common_data)

	# @contextmanager
	# def mock_frappe_calls(self):
	# 	"""Fixture that mocks common Frappe calls"""
	# 	with patch('frappe.get_value') as mock_get_value, \
	# 		patch('frappe.get_all') as mock_get_all, \
	# 		patch('frappe.new_doc') as mock_new_doc:
			
	# 		mock_get_value.return_value = 'TEST'
	# 		yield {
	# 			'get_value': mock_get_value,
	# 			'get_all': mock_get_all,
	# 			'new_doc': mock_new_doc
	# 		}

	# ===============================
	# CONTROLLERS
	# ===============================

	def test_validate(self):
		self.lease.docstatus = 1

		self.fail("This should be covered by a number of cases.")

	def test_before_submit(self):
		self.fail("Unit: check that it calls next_period. \
			Integration: Check that this fails on Draft or Cancelled Rooms")

	# ===============================
	# PROPERTIES
	# ===============================

	def test_total_owing(self):
		self.fail("Unit and Integration. If I mock, I'm testing the summing. \
			If not, I'm testing the biz logic.")


	@patch('frappe.get_cached_value')
	def test_total_paid(self):
		"""Test total_paid property calculates sum of all payments correctly"""
		# Setup test data
		self.lease.payments = [
			frappe._dict({'payment_entry': 'PAY001'}),
			frappe._dict({'payment_entry': 'PAY002'}),
		]
		
		# Mock frappe's database layer more generally
		test_payments = {
			'PAY001': {'paid_amount': 1000},
			'PAY002': {'paid_amount': 500},
		}
		
		def mock_db_get(*args, **kwargs):
			"""Simulate database responses without caring about specific function used"""
			if len(args) >= 1:
				payment_id = args[0]
				return test_payments[payment_id]['paid_amount']
			return None

		# Apply the mock to both potential functions
		with patch('frappe.get_value', mock_db_get), \
			 patch('frappe.get_cached_value', mock_db_get):
			self.assertEqual(self.lease.total_paid, 1500)

	@patch('frappe.get_cached_value')
	def test_outstanding_balance(self, mock_get_cached_value):
		"""Test outstanding_balance property calculates total outstanding correctly"""
		# Setup test data
		self.lease.periods = [
			frappe._dict({'invoice': 'INV001'}),
			frappe._dict({'invoice': 'INV002'}),
		]
		
		test_invoices = {
			'INV001': {'outstanding_amount': 500},
			'INV002': {'outstanding_amount': 300},
		}
		
		def mock_db_get(*args, **kwargs):
			"""Simulate database responses without caring about specific function used"""
			if len(args) >= 1:
				invoice_id = args[0]
				return test_invoices[invoice_id]['outstanding_amount']
			return None

		# Apply the mock to both potential functions
		with patch('frappe.get_value', mock_db_get), \
			 patch('frappe.get_cached_value', mock_db_get):
			self.assertEqual(self.lease.outstanding_balance, 800)


	def test_rental_rate(self):
		self.fail("Integration: Relies on Room.")

	# ===============================
	# PUBLIC INSTANCE METHODS
	# ===============================

	def test_next_period(self):
		self.fail("Unit: Confirm that LeasePeriod is being called.\
			Integration: Confirm business logic of dates.")

	def test_offboard(self):
		self.fail("Unit: Confirm that offboarding occurs? Maybe not even worth.")

	def test_unpaid_periods(self):
		self.fail("Unit: Mock for children.")

	def test_latest_period(self):
		self.fail("Unit: Mock for children.")


	def test_remind_tenant(self):
		self.fail("Not Implemented")


	def test_receive_payment(self):
		self.fail("Unit: Confirm Paymentn is called. \
			Integration: Confirm business logic of LeasePayment.")


	def test_set_status(self):
		self.fail("Unit: Mock for children, with a range of cases.")

	# ===============================
	# STATIC METHODS
	# ===============================

	def test_total_weeks(self):
		"""Test the static method for calculating total weeks between dates"""
		test_cases = [
			# start_date, end_date, expected_weeks
			('2024-01-01', '2024-01-08', 1.0),
			('2024-01-01', '2024-01-15', 2.0),
			('2024-01-01', '2024-01-04', 0.42857142857142855),  # 3 days
		]

		for start_date, end_date, expected in test_cases:
			with self.subTest(start_date=start_date, end_date=end_date):
				result = Lease.total_weeks(start_date, end_date)
				self.assertAlmostEqual(result, expected, places=5)

	def test_autorenew(self):
		self.fail("Hmmm, several test cases.")


	def test_calculate_renewal_buffer(self):
		"""Test the static method for calculating renewal buffer dates"""
		test_cases = [
			# period_end, expected_buffer
			('2024-01-15', '2024-01-01'),  # normal case
			('2024-01-01', '2023-12-18'),  # year boundary
			('2024-02-01', '2024-01-18'),  # month boundary
			('2024-03-14', '2024-02-29'),  # leap year
			('2025-03-14', '2025-02-28'),  # non leap year
		]

		for period_end, expected in test_cases:
			with self.subTest(period_end=period_end):
				result = Lease.calculate_renewal_buffer(period_end)
				self.assertEqual(result, expected)

	def test_renew_date(self):
		self.fail("Several test cases..?")
# ========================================


class TestLeasePeriodUnit(FrappeTestCase):
	"""Unit Tests for Lease Period.
	Focuses on mocking static and public instance methods with mocks."""

	# ===============================
	# CONTROLLERS
	# ===============================
	# Validate
	# Status

	# ===============================
	# STATIC METHODS
	# ===============================


	def test_next_period(self):
		self.fail("Several test cases..?")


	def test_new_invoice_item(self):
		self.fail("Several test cases..?")


	def test_new_sales_invoice(self):
		self.fail("Several test cases..?")
	
class TestLeaseIntegration(FrappeTestCase):
	def setUp(self):
		# Create test records
		self.test_room = create_test_room()
		self.test_customer = create_test_customer()
		self.test_shop = create_test_shop()
		
		# Create a basic lease for testing
		self.lease = create_test_lease(
			leasing_of=self.test_room.name,
			leased_from=self.test_shop.name,
			start_date=today(),
			end_date=add_months(today(), 3),
			period_length="Monthly"
		)

	def tearDown(self):
		# Clean up test records
		for doctype in ['Lease', 'Room', 'Customer', 'Shop']:
			frappe.db.delete(doctype)

	# =================================
	# Mocking Sample Code
	# =================================

	@patch('frappe.get_value')
	@patch.object(Lease, 'create_submit_sales_order')
	@patch.object(Lease, 'create_submit_sales_invoice')
	@patch.object(Lease, 'save_append_to_transactions')
	@patch.object(Lease, 'save_move_next_date')
	def test_create_lease_transaction(self, mock_save_move_next_date, mock_save_append_to_transactions, 
									  mock_create_submit_sales_invoice, mock_create_submit_sales_order, 
									  mock_get_value):
		# Mock frappe.get_value for Shop's owned_by
		mock_get_value.return_value = "TEST-CUSTOMER-001"

		# Mock Sales Order
		mock_so = MagicMock()
		mock_so.name = "SO-001"
		mock_create_submit_sales_order.return_value = mock_so

		# Mock Sales Invoice
		mock_si = MagicMock()
		mock_si.name = "SI-001"
		mock_create_submit_sales_invoice.return_value = mock_si

		# Call the method to test
		self.lease.create_lease_transaction()

		# Assertions
		mock_get_value.assert_called_once_with('Shop', 'TEST-SHOP-001', 'owned_by')
		mock_create_submit_sales_order.assert_called_once()
		mock_create_submit_sales_invoice.assert_called_once_with(mock_so)
		mock_save_append_to_transactions.assert_called_once_with(mock_so, mock_si, None)
		mock_save_move_next_date.assert_called_once()

	def test_validate_room_availability(self):
		"""Test that leases can't be created for unavailable rooms"""
		# Create a lease for the same room
		with self.assertRaises(frappe.ValidationError):
			create_test_lease(
				leasing_of=self.test_room.name,
				leased_from=self.test_shop.name,
				start_date=today(),
				end_date=add_months(today(), 3)
			)

	def test_validate_dates(self):
		"""Test date validation logic"""
		# Test end date before start date
		with self.assertRaises(frappe.ValidationError):
			create_test_lease(
				leasing_of=self.test_room.name,
				start_date=today(),
				end_date=add_days(today(), -1)
			)

		# Test backdated start date
		with self.assertRaises(frappe.ValidationError):
			create_test_lease(
				leasing_of=self.test_room.name,
				start_date=add_months(today(), -2),
				end_date=add_months(today(), 3)
			)

	def test_period_calculations(self):
		"""Test period-related calculations"""
		# Test monthly period
		monthly_lease = create_test_lease(period_length="Monthly")
		self.assertEqual(monthly_lease.period_weeks(), 4)

		# Test quarterly period
		quarterly_lease = create_test_lease(period_length="Quarterly")
		self.assertEqual(quarterly_lease.period_weeks(), 12)

	def test_financial_calculations(self):
		"""Test financial calculations with mock data"""
		lease = create_test_lease()
		
		# Mock period with invoice
		period = frappe.get_doc({
			"doctype": "Lease Period",
			"parent": lease.name,
			"invoice": "TEST-INV-001"
		})
		lease.append("periods", period)
		
		# Mock payment
		payment = frappe.get_doc({
			"doctype": "Lease Payment",
			"parent": lease.name,
			"payment_entry": "TEST-PAY-001"
		})
		lease.append("payments", payment)

		with patch('frappe.get_cached_value') as mock_get_value:
			# Mock invoice amount
			mock_get_value.side_effect = lambda doctype, name, field: {
				('Sales Invoice', 'TEST-INV-001', 'grand_total'): 1000,
				('Sales Invoice', 'TEST-INV-001', 'outstanding_amount'): 400,
				('Payment Entry', 'TEST-PAY-001', 'paid_amount'): 600
			}.get((doctype, name, field))

			self.assertEqual(lease.total_owing, 1000)
			self.assertEqual(lease.total_paid, 600)
			self.assertEqual(lease.outstanding_balance, 400)

	def test_status_updates(self):
		"""Test lease status updates based on period statuses"""
		lease = create_test_lease()
		
		# Test Active status
		period1 = frappe.get_doc({
			"doctype": "Lease Period",
			"parent": lease.name,
			"status": "Paid"
		})
		lease.append("periods", period1)
		lease.set_status()
		self.assertEqual(lease.status, "Active")

		# Test Overdue status
		period2 = frappe.get_doc({
			"doctype": "Lease Period",
			"parent": lease.name,
			"status": "Overdue"
		})
		lease.append("periods", period2)
		lease.set_status()
		self.assertEqual(lease.status, "Overdue")

	# Add individual tests for create_submit_sales_order, create_submit_sales_invoice, etc.