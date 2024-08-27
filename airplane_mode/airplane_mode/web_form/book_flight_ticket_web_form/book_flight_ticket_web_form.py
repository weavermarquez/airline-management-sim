import frappe

def get_context(context):
	# do your magic here
	context.my_price = 1234
	context.flight = frappe.form_dict.flight if frappe.form_dict.flight else None


# On Load:
# Set Price to anything
# Auto-set the Flight based on the origin page
