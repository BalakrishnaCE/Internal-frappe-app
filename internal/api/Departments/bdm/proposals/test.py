import frappe

@frappe.whitelist(allow_guest=True)
def get_data():
    doc = frappe.get_doc("Lead", "LEADID00286951")
    return doc