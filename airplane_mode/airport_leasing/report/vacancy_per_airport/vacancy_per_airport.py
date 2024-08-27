# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data

def get_sql_call():
	result = frappe.db.sql(
		f"""
		SELECT `path`,
				COUNT(*) as count,
				COUNT(CASE WHEN CAST(`is_unique` as Integer) = 1 THEN 1 END) as unique_count
		FROM `tabWeb Page View`
		WHERE `creation` BETWEEN {some_date} AND {some_later_date}
		"""
	)
	pass