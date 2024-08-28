# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class AirplaneTicketAddonType(Document):
	pass

@frappe.whitelist()
def create_duplicate(doc: str):
	# Create a duplicate of this doctype with slightly altered Name and a child item in 
	doc_dict = json.loads(doc)
	addon_type = frappe.new_doc('Airplane Ticket Add-on Type', 
		name = "Testing Type",
		critical_east = 1,
		options = []
	)

	# Method 1
	child = frappe.new_doc('Airplane Ticket Add-on Option')
	child.update({
		'option': "Testing",
		'risk_score': 5,
		'uncertainty_score': 5
	})

	# Method 2
	# child = frappe._dict({
	# 	'item_code': doc_dict['leasing_of'],
	# 	'delivery_date': doc_dict['start_date'],
	# 	'quantity': num_of_weeks
	# 	})

	addon_type.append('options', child)

	addon_type.insert()
	# TODO Try using different settings on insert
	# NOTE It didn't work :cry:
	# doc.insert(
	# 	ignore_permissions=True, # ignore write permissions during insert
	# 	ignore_links=True, # ignore Link validation in the document
	# 	ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
	# 	ignore_mandatory=True # insert even if mandatory fields are not set
	# )

	frappe.msgprint(
		msg='Add-on Type "%s" duplicated.' % (addon_type.name),
		title='Add-on Type Duplication',
		indicator='green')

	return True