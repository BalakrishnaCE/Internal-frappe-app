import frappe
import json
from frappe.utils import get_datetime

@frappe.whitelist()
def get_leads():
    return frappe.db.sql("""
        SELECT
            vp.name as id,
            vp.name1 as name,
            vp.company,
            vp.mobile_number,
            vp.email_id,
            vp.lead_type,
            vp.date_and_time_of_visit,
            vp.visit_location1,
            vp.visit_created_by_pre_sales,
            vp.assigned_to,
            vp.creation,
            vp.claimed_by,
            vp.claimed_on,
            vp.removed_by
        FROM `tabVisiting Prospects` vp
        JOIN `tabLeads` l ON l.name = vp.name
        WHERE
            (vp.claimed_by IS NULL OR vp.claimed_by = '')
            AND (vp.claimed_on IS NULL OR vp.claimed_on = '')
            AND (vp.removed_by IS NULL OR vp.removed_by = 0)
            AND l.leasing_status IN ('Prospect', 'Active Prospect')
    """, as_dict=True)


@frappe.whitelist()
def get_leads_by_id():
    lead_id = frappe.form_dict.get("lead_id")
    if not lead_id:
        frappe.throw("Missing required parameter: lead_id")

    fields = [
        'name as id',
        'name1 as name',
        'company',
        'mobile_number',
        'email_id',
        'lead_type',
        'date_and_time_of_visit',
        'visit_location1',
        'visit_created_by_pre_sales',
        'assigned_to',
        'creation',
        'claimed_by',
        'claimed_on',
        'removed_by'
    ]

    data = frappe.get_all('Visiting Prospects', filters={'name': lead_id}, fields=fields, limit=1)
    return data[0] if data else {}


@frappe.whitelist()
def get_audio():
    return json.loads(frappe.request.data)


@frappe.whitelist()
def claim_lead():
    debug_info = []
    data = frappe.form_dict
    lead_id = data.get("lead_id")
    pre_sales = data.get("pre_sales")
    claimed_by = data.get("claimed_by")
    child_fields_dict = data.get("child_fields_dict")
    office_type = data.get("officeType")

    debug_info.append(f"Incoming: lead_id={lead_id}, pre_sales={pre_sales}, claimed_by={claimed_by}, officeType={office_type}, child_fields_dict={child_fields_dict}")

    if not lead_id or not claimed_by:
        frappe.response['message'] = "Missing required parameters: lead_id, claimed_by"
        frappe.response['debug'] = '\n'.join(debug_info)
        return

    try:
        str_to_dict = json.loads(child_fields_dict) if child_fields_dict else {}
        debug_info.append(f"Parsed child_fields_dict: {str_to_dict}")

        # Visiting Prospects doc
        visit_doc = frappe.get_doc('Visiting Prospects', lead_id)
        debug_info.append(f"Fetched Visiting Prospects doc: {lead_id}")

        if visit_doc.claimed_by:
            frappe.response['message'] = f'This Lead has already been claimed by {visit_doc.claimed_by}'
            debug_info.append(f"Already claimed: {lead_id} by {visit_doc.claimed_by}")
            frappe.response['debug'] = '\n'.join(debug_info)
            return

        visit_doc.claimed_by = claimed_by
        visit_doc.claimed_on = get_datetime()
        visit_doc.save(ignore_permissions=True)
        debug_info.append(f"Saved Visiting Prospects: {lead_id}")

        # Leads doc
        lead_doc = frappe.get_doc('Leads', lead_id)
        debug_info.append(f"Fetched Leads doc: {lead_id}")

        lead_doc.assignedto = claimed_by
        lead_doc.pre_sales_assigned_user = pre_sales
        debug_info.append("Updated assignedto and pre_sales_assigned_user in Leads")

        manager_id = frappe.db.get_value('Employee', {'user_id': claimed_by}, 'reports_to')
        if manager_id:
            manager_email = frappe.db.get_value('Employee', manager_id, 'user_id')
            if manager_email:
                lead_doc.managedby = manager_email
                debug_info.append(f"Set managedby in Leads: {manager_email}")

        if office_type == "Office" and str_to_dict:
            lead_doc.append('visit_details', str_to_dict)
            debug_info.append("Appended visit_details to Leads")

        lead_doc.save(ignore_permissions=True)
        debug_info.append(f"Saved Leads doc: {lead_id}")

        frappe.db.commit()
        debug_info.append("Committed DB changes")

        frappe.publish_realtime(event='lead_claimed', message=lead_id)
        debug_info.append("Published realtime event")

        frappe.response['message'] = 'Lead Claimed Successfully'
        frappe.response['debug'] = '\n'.join(debug_info)

    except Exception as e:
        debug_info.append(f"Exception: {str(e)}")
        debug_info.append(frappe.get_traceback())
        frappe.response['message'] = f"Error: {str(e)}"
        frappe.response['debug'] = '\n'.join(debug_info)


@frappe.whitelist()
def remove_lead():
    data = frappe.form_dict
    lead_id = data.get("lead_id")
    removed_by = data.get("removed_by")

    if not (lead_id and removed_by):
        frappe.throw("Missing required parameters: lead_id, removed_by")

    frappe.db.set_value("Visiting Prospects", lead_id, {"removed_by": removed_by})
    frappe.db.commit()
    return {"message": "Lead marked as removed."}


