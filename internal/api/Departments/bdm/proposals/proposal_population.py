import frappe
import json
import datetime
from internal.api.Departments.bdm.visiting_leads import get_leads


@frappe.whitelist(allow_guest=True)
def create_proposal(data):
    lead_id = data.get("lead_id")
    if not lead_id:
        frappe.throw("Missing lead_id in proposal data")
    doc = frappe.get_doc("Leads",lead_id)
    items = data.get("items", [])
    if not isinstance(items, list):
        frappe.throw("Items must be a list")
    for item in items:
        if not item:
            continue
        if item['recursionType'] == "seats":
            child = doc.append("item", {})
            child.item_code = item["productName"]
            child.sales_description = item["salesDescription"]
            child.start_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.stop_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.novel_billing_entity="Millertech Spaces LLP"
            child.rollout_status = "CRF&MAF"
            child.qty = item["qty"]
            child.rate = item["ratePerUnit"]
            child.amount = item["qty"] * item["ratePerUnit"]
        if item['recursionType'] == "amenities":
            child = doc.append("amenity_recursion", {})
            child.item_code = item["productName"]
            child.sales_description = item["salesDescription"]
            child.start_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.stop_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.novel_billing_entity="Millertech Spaces LLP"
            child.qty = item["qty"]
            child.rate = item["ratePerUnit"]
            child.amount = item["qty"] * item["ratePerUnit"]
    doc.save(ignore_permissions=True)
    return {"name": doc.name1}


@frappe.whitelist(allow_guest=True)
def submit_proposal():
    raw_data = frappe.request.get_data()

    if not raw_data:
        frappe.throw("No data received in request")

    try:
        json_str = raw_data.decode("utf-8")
        data = json.loads(json_str)
    except Exception as e:
        frappe.throw(f"Error parsing request data: {e}")

    if not data:
        frappe.throw("Parsed data is empty or invalid")
        
    proposal_id = create_proposal(data)
    return {"status": "success", "proposal_id": proposal_id}


