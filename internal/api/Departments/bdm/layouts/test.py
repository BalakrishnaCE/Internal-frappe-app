import frappe 
import json

@frappe.whitelist(allow_guest=True)
def get_leads():
    doc = frappe.db.get_list("Leads", fields=["name", "name1", "company"], limit=100)
    return doc

@frappe.whitelist(allow_guest=True)
def get_Users():
    doc = frappe.db.get_list("User", limit=100)
    return doc

@frappe.whitelist(allow_guest=True)
def get_user_by_email(email):
    doc = frappe.db.get_value("User", email, ["name", "full_name", "last_login"], as_dict=True)
    return doc

@frappe.whitelist(allow_guest=False)
def update_user_full_name(email, new_full_name):
    frappe.db.set_value("User", email, "full_name", new_full_name)
    return {"status": "success"}
