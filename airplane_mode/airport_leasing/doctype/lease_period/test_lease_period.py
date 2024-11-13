import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, Mock, MagicMock
from datetime import date
from airplane_mode.airport_leasing.doctype.lease_period.lease_period import LeasePeriod

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

class TestLeasePeriod(FrappeTestCase):

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# cls.common_data = {
		# 	'leasing_of' : 'ROOM-001',
		# 	'leased_from' : 'COMPANY-001',
		# 	'leased_to' : 'SHOP-001',
		# 	'period_weeks.return_value' : 4,  # Monthly
		# 	'start_date' : '2024-01-01',
		# 	'end_date' : '2024-12-31'
		# 	}

	def setUp(self):
		self.lease = Mock()
		# self.lease = Mock(**cls.common_data)

		self.lease.leasing_of = "ROOM-001"
		self.lease.leased_from = "COMPANY-001"
		self.lease.leased_to = "SHOP-001"
		self.lease.period_weeks.return_value = 4  # Monthly
		self.lease.start_date = "2024-01-01"
		self.lease.end_date = "2024-12-31"
		
	def test_get_period_start_date_first_period(self):
		"""Test start date calculation for first period"""
		self.lease.periods = []
		
		start_date = LeasePeriod._get_period_start_date(self.lease)
		
		self.assertEqual(start_date, "2024-01-01")

	def test_get_period_start_date_subsequent_period(self):
		"""Test start date calculation for subsequent period"""
		last_period = Mock(end_date="2024-01-29")
		self.lease.periods = [last_period]
		self.lease.latest_period.return_value = last_period
		
		start_date = LeasePeriod._get_period_start_date(self.lease)
		
		self.assertEqual(start_date, "2024-01-30")

	def test_get_period_end_date_normal(self):
		"""Test end date calculation within lease period"""
		start_date = "2024-01-01"
		
		end_date = LeasePeriod._get_period_end_date(self.lease, start_date)
		
		self.assertEqual(end_date, "2024-01-29")  # 4 weeks later

	def test_get_period_end_date_at_lease_end(self):
		"""Test end date calculation when period would exceed lease end"""
		self.lease.end_date = "2024-01-15"
		start_date = "2024-01-01"
		
		end_date = LeasePeriod._get_period_end_date(self.lease, start_date)
		
		# Should be limited by lease end date
		self.assertEqual(end_date, "2024-01-15")

	@patch('frappe.get_value')
	def test_create_period_invoice(self, mock_get_value):
		"""Test invoice creation with all components"""
		mock_get_value.return_value = "CUSTOMER-001"
		dates = {
			'start_date': "2024-01-01",
			'end_date': "2024-01-29"
		}
		
		with patch.object(LeasePeriod, 'new_invoice_item') as mock_new_item, \
			 patch.object(LeasePeriod, 'new_sales_invoice') as mock_new_invoice:
			
			LeasePeriod.create_period_invoice(self.lease, dates)
			
			# Verify correct item creation
			mock_new_item.assert_called_once_with(
				room="ROOM-001",
				start_date="2024-01-01",
				weeks=4
			)
			
			# Verify invoice creation
			mock_new_invoice.assert_called_once()

