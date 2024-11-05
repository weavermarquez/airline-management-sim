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

class TestMockLearns(FrappeTestCase):

	def test_mock_basic(self):
		foo = MagicMock(return_value=3)
		value = foo(3, 4, 5, key='value')
		foo.assert_called_with(3, 4, 5, key='value')
		self.assertEqual(value, 3)

	def test_side_effect_error(self):
		mock = Mock(side_effect=KeyError('foo'))
		def bluh():
			return 1
		self.assertRaises(KeyError, mock)
		# Regular error if unexpected exception
		# Failure if no exception

	def test_side_effect_error_cm(self):
		mock = Mock(side_effect=KeyError('foo'))
		with self.assertRaises(KeyError, msg='UWU') as cm:
			mock()
		exception = cm.exception
		self.assertEquals(exception.args, ('foo', ))
		self.assertEquals(cm.msg, 'UWU')

	def test_side_effect_function(self):
		def side_effect(arg):
			return values[arg]

		values = {'a': 1, 'b': 2, 'c': 3}

		mock = Mock()
		mock.side_effect = side_effect

		(a,b,c) = mock('a'), mock('b'), mock('c')
		# (1, 2, 3)
		self.assertEquals((a,b,c), (1,2,3))

		mock.side_effect = [5, 4, 3, 2, 1]

		(a,b,c) = mock(), mock(), mock()
		self.assertEquals((a,b,c), (5,4,3))


	#
	# patch('path.to.Class') patches the dot.name.constructor.
	#

	def make_airport_uwu(self):
		instance = frappe.new_doc('Airport', **self.foo_dict)
		assert isinstance(instance, Airport)
		assert not isinstance(instance.uwu, Mock)
		assert not isinstance(instance, Mock)
		return instance.uwu()
		# module.foo

	# NOTE Fails because this is attempting to mock the Constructor and Module.
	def test_patch_new_doc(self):
		with patch('airplane_mode.airplane_mode.doctype.airport.airport.Airport') as mock:
			instance = mock.return_value
			instance.uwu.return_value = 'the result'

			result = self.make_airport_uwu()
			self.assertEquals(result, 'the result')



	def make_airport_owo(self):
		instance = Airport(doctype='Airport', **self.foo_dict)
		assert isinstance(instance, Airport)
		assert not isinstance(instance.owo, Mock)
		assert not isinstance(instance, Mock)

		print(f"OWO: Airport.owo is Mock?: {isinstance(instance.owo, Mock)}")
		return instance.owo()
		# module.foo

	def test_patch_class_constructor_full(self):
		with patch('airplane_mode.airplane_mode.doctype.airport.airport.Airport') as mock:
			instance = mock.return_value
			instance.owo.return_value = 'the result'

			result = self.make_airport_owo()
			self.assertEquals(result, 'the result')



	def make_airport_awa(self):
		import airplane_mode
		instance = airplane_mode.airplane_mode.doctype.airport.airport.Airport(
			doctype='Airport', **self.foo_dict)
		assert isinstance(instance, Mock)
		assert isinstance(instance.awa, Mock)
		assert not isinstance(instance, Airport)

		return instance.awa()
		# module.foo

	def test_patch_class_constructor_module(self):
		with patch('airplane_mode.airplane_mode.doctype.airport.airport.Airport') as mock:
			instance = mock.return_value
			instance.awa.return_value = 'the result'

			result = self.make_airport_awa()
			self.assertEquals(result, 'the result')


	#
	# Patching /local/ Airport
	#

	def instantiate_airport_frappe(self) -> Airport:
		airport = frappe.new_doc('Airport', **self.foo_dict)
		return airport

	# @patch('airplane_mode.airport_leasing.doctype.room.test_room.Airport')
	@patch('airplane_mode.airplane_mode.doctype.airport.airport.Airport')
	def test_patch_local_airport_frappe(self, MockAirport):
		airport = frappe.new_doc('Airport', **self.foo_dict)
		# airport = self.instantiate_airport_frappe()
		print(f"MockAirport is type {type(MockAirport)}")
		print(f"airport is type {type(airport)}")
		self.assert_(isinstance(airport, MockAirport))



	def instantiate_airport_constructor(self) -> Airport:
		airport = Airport(doctype='Airport', **self.foo_dict)
		return airport

	@patch('airplane_mode.airport_leasing.doctype.room.test_room.Airport')
	def test_patch_local_airport_constructor(self, MockAirport):
		airport = self.instantiate_airport_constructor()
		self.assert_(isinstance(airport, MockAirport))


	#
	# patch.object()
	#
	def test_patch_object_frappe(self):
		with patch.object(Airport, 'uwu', return_value=None) as mock_method:
			thing = frappe.new_doc('Airport', **self.foo_dict)
			thing.uwu(1, 2, 3)
			assert isinstance(thing, Airport)
			assert isinstance(thing.uwu, Mock)
			assert not isinstance(thing, Mock)
		mock_method.assert_called_once_with(1, 2, 3)	
		

	def test_patch_object_constructor(self):
		with patch.object(Airport, 'uwu', return_value=None) as mock_method:
			thing = Airport(doctype='Airport', **self.foo_dict)
			thing.uwu(1, 2, 3)
			# True

			assert isinstance(thing, Airport)
			assert isinstance(thing.uwu, Mock)
			assert not isinstance(thing, Mock)
		mock_method.assert_called_once_with(1, 2, 3)

	# NOTE Fails because it begins from toplevel.
	def test_patch_object_module_name(self):
		with patch('airport.Airport') as mock:
			instance = mock.return_value
			instance.uwu.return_value = 'the result'

			result = self.make_airport_uwu()
			self.assertEquals(result, 'the result')


	def tearDown(self):
		frappe.delete_doc_if_exists('Airport', self.airport.name, 1)
		frappe.delete_doc_if_exists('Room', self.room.name, 1)


	def test_autoname(self):
		expected_room_name = f"{self.airplane_code}{self.room_number}"
		self.assertEqual(self.room.name, expected_room_name)


	def test_item_created_with_default_rate(self):
		self.assertEqual(1,1)
		default_rate = 5000
		settings = frappe.get_doc('Airport Leasing Settings')
		settings.default_rental_rate = default_rate
		settings.save()

		# self.room.submit()
		self.room.on_submit()
		# Check that item exists
		item_code = self.room.room_name()
		item_exists = frappe.db.exists('Item', item_code)
		if not item_exists:
			self.fail('Item does not exist')
		self.assertEqual(frappe.get_doc('Item', item_code).standard_rate, default_rate)


