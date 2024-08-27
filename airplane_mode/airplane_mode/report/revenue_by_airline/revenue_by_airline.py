# Copyright (c) 2024, Weaver Marquez and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	message = "OwO"
	chart = get_chart(data)
	report_summary = get_summary(data)
	return columns, data, message, chart, report_summary

def get_data(filters=None):
	"""Finds total revenue for all Airlines from Airplane Tickets"""

	airline_names = frappe.db.get_list('Airline', pluck='name')
	data = []
	for airline in airline_names:
		revenue = get_revenue(airline, filters)
		row = {'airline': airline, 'revenue': revenue}

		data.append(row)

	return data


# Ah, but total_price is a Virtual Field. So, SQL calls don't work.
# Get a list of Tickets
# Ticket has flight

# What if we got a list of Flights
# What if we got a list of Tickets grouped by Airline
# flight has airplane
# airplane has airline

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

def get_revenue(airline, filters=None):
	"""For an Airline, grab the revenue"""

	plane_names = get_airplanes_per_airline(airline, filters)
	revenue = 0
	for plane in plane_names:
		flights = get_flights_per_airplane(plane)
		for flight in flights:
			revenue += get_revenue_per_flight(flight, filters)
	return revenue

def get_revenue_per_flight(flight, filters=None):
	"""Return list of ticket revenues per Airplane Flight"""

	if filters.booked:
		# somehow affect the get_list
		pass
	flight_revenue = frappe.db.get_list('Airplane Ticket',
		filters={'flight': flight}, # Tickets must be booked. 'docstatus': 1
		pluck='total_amount'
	)
	return sum(flight_revenue)

def get_flights_per_airplane(airplane):
	"""Returns a list of Airplane Flights that belong to an airplane"""

	flights = frappe.db.get_list('Airplane Flight',
		filters={'airplane': airplane},
		pluck='name'
	)
	return flights
	

def get_airplanes_per_airline(airline, filters):
	"""Returns a list of airplanes that belong to an airline."""

	planes = frappe.db.get_list('Airplane',
		filters={'airline': airline},
		fields=['name', 'airline'],
		pluck='name'
	)
	return planes


def get_columns():
	columns = [
		{
			'label': 'Airline',
			'fieldtype': 'Link',
			'fieldname': 'airline',
			'options': 'Airline',
			'width': 300
		},
		{
			'label': 'Revenue',
			'fieldtype': 'Currency',
			'fieldname': 'revenue',
			'width': 300
		}
	]
	return columns

def get_chart(data):
	labels = [d.get('airline') for d in data]

	revenues = [d.get('revenue') for d in data]

	datasets = [{'name': 'Revenues', 'values': revenues}]
	chart = {'data': {'labels': labels, 'datasets': datasets}}
	chart['type'] = 'donut'

	return chart

def get_summary(data):
	# Total Revenue
	total_revenue = get_total_revenue_from_data(data)
	frappe.errprint(total_revenue)

	return [ {
		"value": total_revenue,
		"indicator": "Green" if total_revenue > 0 else "Red",
		"label": "Total Revenue",
		"datatype": "Currency"
	} ]

def get_total_revenue_from_data(data):
	total_revenue = 0
	for d in data:
		total_revenue += d.get("revenue")
	return total_revenue
# show how much revenue each Airline has made.

# Here are some properties of this report:
#     has a summary section which shows the Total Revenue. 
#     It also has a total row.
#     Airline is a Link type column and revenue is a Currency type column.
#     Even Airlines with 0 revenue are included.
