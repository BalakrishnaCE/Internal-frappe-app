# NOTE: The following uses Frappe APIs. Linter may not recognize 'frappe.whitelist', 'frappe.form_dict', 'frappe.get_all', or 'frappe.db', but these are valid in Frappe framework.

import frappe
from internal.api.Departments.bdm.visiting_leads import get_leads_by_id

@frappe.whitelist(allow_guest=True)
def get_mafID(lead_id_or_name=None):
    if not lead_id_or_name:
        lead_id_or_name = frappe.form_dict.get('lead_id_or_name')
    if not lead_id_or_name:
        return {}

    # If not a lead id, resolve from Leads doctype
    if not lead_id_or_name.startswith('LEAD'):
        # Try to fetch the lead id by name from Leads doctype
        lead_data = frappe.get_all('Leads', filters={'lead_name': lead_id_or_name}, fields=['name'], limit=1)
        if lead_data:
            lead_id_or_name = lead_data[0]['name']
        else:
            return {}
    result = frappe.db.sql("""
        SELECT
            name,
            owner,
            creation,
            modified,
            modified_by,
            docstatus,
            idx,
            link_in,
            update1,
            maf_client_id,
            form_url,
            type_of_customer,
            customer_email,
            agreement_entered,
            place,
            company2,
            rate1,
            company_address,
            customer,
            location,
            authorized_name,
            cr_email,
            subject,
            rollout,
            rental_es,
            maf_send_mail,
            term_of_maf,
            term_commencement_date,
            term_end_date,
            handover_date,
            security_deposit,
            lockinperiod,
            noticeperiod,
            mr,
            cr,
            mr_or_cr,
            bdm_email,
            email_sent,
            update_clause
        FROM `tabMAF Document`
        WHERE link_in = %s
        LIMIT 1
    """, (lead_id_or_name,), as_dict=True)
    return result[0] if result else {}