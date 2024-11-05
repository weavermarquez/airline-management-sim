import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch, Mock

from airplane_mode.airport_leasing.doctype.lease_payment.lease_payment import LeasePayment

class TestLeasePayment(FrappeTestCase):
	"""Unit Tests for Lease Payment.
	Focuses on mocking static and public instance methods with mocks."""
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.common_data = {
			'invoice' : 'INV-001',
			'reference_no' : 'REF123',
		}

	def setUp(self):
		self.lease = Mock()
		self.lease.latest_period.return_value = Mock(invoice=self.common_data['invoice'])

	# def test_new_payment(self):
	# 	self.fail("Several test cases..?")
		
	@patch('airplane_mode.airport_leasing.doctype.lease_payment.lease_payment.get_payment_entry')
	def test_new_payment_entry_success(self, mock_get_payment_entry):
		"""Test successful creation of payment entry"""
		# Setup
		amount = 1000
		reference_no = self.common_data['reference_no']
		mock_payment = Mock()
		mock_get_payment_entry.return_value = mock_payment
		
		# Execute
		LeasePayment.new_payment_entry(self.lease, amount, reference_no)
		
		# Verify
		mock_get_payment_entry.assert_called_once_with(
			'Sales Invoice', 
			self.common_data['invoice'], 
			party_amount=amount,
			reference_date=frappe.utils.today()
		)
		mock_payment.submit.assert_called_once()
		
	def test_new_payment_entry_no_invoice(self):
		"""Test payment entry creation fails when no invoice exists"""
		self.lease.latest_period.return_value = None
		
		with self.assertRaises(frappe.ValidationError):
			LeasePayment.new_payment_entry(self.lease, 1000, self.common_data['reference_no']) 


	# On Trash
