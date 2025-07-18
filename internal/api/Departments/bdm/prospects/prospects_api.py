import frappe

@frappe.whitelist()
def get_prospect_details():
    # user = frappe.session.user
    user = frappe.form_dict.get("user")
    data = frappe.db.sql("""
        SELECT 
            l.name AS id,
            l.name1 AS name,
            l.company AS company,
            v.date_and_time_of_visit AS dateandtime,
            LEFT(UPPER(l.name1), 1) AS initials,
            CASE
                WHEN l.leasing_status IN ('Prospect', 'Active Prospect') THEN 'Todo'
                WHEN l.leasing_status = 'Visited Prospect' THEN 'In Progress'
                ELSE 'Unknown'
            END AS status
        FROM 
            `tabLeads` l
        JOIN 
            `tabVisiting Prospects` v ON v.name = l.name
        WHERE 
            l.leasing_status IN ('Prospect', 'Visited Prospect', 'Active Prospect')
            AND l.assignedto = %s
    """, (user,), as_dict=True)
    return data

@frappe.whitelist()
def get_prospect_journey_details():
    lead = frappe.form_dict.get("prospectId")
    data = frappe.db.sql("""
         SELECT 
        l.name AS id,
        l.leasing_status AS leasing_status, 
        l.name1 AS name, 
        l.company AS company, 
        DATE(v.date_and_time_of_visit) AS visit_date,
        LEFT(UPPER(l.name1), 1) AS initials,
        c.content AS latest_comment
    FROM 
        `tabLeads` l
    JOIN 
        `tabVisiting Prospects` v ON v.name = l.name
    LEFT JOIN (
        SELECT 
            content, reference_name
        FROM 
            `tabComment`
        WHERE 
            comment_type = "Comment"
            AND reference_doctype = "Leads"
            AND reference_name = %s
        ORDER BY 
            creation DESC
        LIMIT 1
    ) c ON c.reference_name = l.name
    WHERE 
        l.name= %s
    """,(lead,lead,),as_dict=True)
    return data

@frappe.whitelist()
def get_comment_history():
    lead = frappe.form_dict.get("prospectId")
    data = frappe.db.sql("""
        SELECT 
            DATE(creation) AS creation_date, 
            content,
            comment_by
        FROM 
            `tabComment`
        WHERE 
            comment_type = 'Comment'
            AND reference_doctype = 'Leads'
            AND reference_name = %s
        ORDER BY 
            creation_date DESC
    """,(lead,),as_dict=True)
    return data

@frappe.whitelist()
def update_leasing_status_on_visit():
    lead = frappe.form_dict.get("lead")
    doc = frappe.get_doc("Leads", lead)
    doc.leasing_status = "Visited Prospect"
    doc.save()
    return doc

@frappe.whitelist()
def update_visit_details():
    lead = frappe.form_dict.get("lead")
    comment = frappe.form_dict.get("comment")
    file_name = frappe.form_dict.get("file_name")
    file_url = frappe.form_dict.get("file_url")
    comment_by = frappe.form_dict.get("comment_by")

    comment_doc = frappe.new_doc("Comment")
    comment_doc.comment_type = "Comment"
    comment_doc.reference_doctype = "Leads"
    comment_doc.reference_name = lead
    comment_doc.content = comment
    comment_doc.comment_by = comment_by
    comment_doc.insert()

    file_doc = frappe.new_doc("File")
    file_doc.file_name = file_name
    file_doc.file_url = file_url
    file_doc.attached_to_doctype = "Leads"
    file_doc.attached_to_name = lead
    file_doc.save()
    return "Success"



@frappe.whitelist()
def update_visit_details():
    import os
    import json

    lead = frappe.form_dict.get("lead")
    comment = frappe.form_dict.get("comment")
    file_names = frappe.form_dict.get("file_name")
    file_urls = frappe.form_dict.get("file_url")
    comment_by = frappe.form_dict.get("comment_by")

    if isinstance(file_names, str):
        try:
            file_names = json.loads(file_names)
        except:
            file_names = [file_names]
    
    if isinstance(file_urls, str):
        try:
            file_urls = json.loads(file_urls)
        except:
            file_urls = [file_urls]

    frappe.logger().info(f"Lead: {lead}, File Names: {file_names}, File URLs: {file_urls}, Comment By: {comment_by}")

    comment_content = comment
    if file_names and len(file_names) > 0 and file_names[0].strip():
        comment_content += f"\n\nAttached Files:\n"
        for i, file_name in enumerate(file_names):
            if file_name.strip():
                file_url = file_urls[i] if i < len(file_urls) else ""
                comment_content += f"- {file_name}"
                if file_url:
                    comment_content += f" ({file_url})"
                comment_content += "\n"

    comment_doc = frappe.new_doc("Comment")
    comment_doc.comment_type = "Comment"
    comment_doc.reference_doctype = "Leads"
    comment_doc.reference_name = lead
    comment_doc.content = f"Visit Comment: {comment_content}"
    comment_doc.comment_by = comment_by
    comment_doc.insert()

    if file_names and len(file_names) > 0:
        for i, file_name in enumerate(file_names):
            if file_name.strip():
                file_url = file_urls[i] if i < len(file_urls) else ""
                if file_url:
                    try:
                        file_doc = frappe.get_doc("File", {"file_url": file_url})
                        if not file_doc.attached_to_doctype or file_doc.attached_to_doctype != "Leads":
                            file_doc.attached_to_doctype = "Leads"
                            file_doc.attached_to_name = lead
                            file_doc.is_private = 0
                            file_doc.save()
                            frappe.logger().info(f"File {file_name} properly attached to Lead {lead}")
                    except frappe.DoesNotExistError:
                        frappe.logger().warning(f"File document not found for URL: {file_url}")
                    except Exception as e:
                        frappe.logger().error(f"Error processing file {file_name}: {str(e)}")

    frappe.logger().info(f"Comment and file attachments saved successfully for lead: {lead}")
    return "Success"


@frappe.whitelist()
def get_files():
    lead = frappe.form_dict.get("lead")
    data = frappe.db.sql("""
        select file_name,file_url
        from `tabFile` 
        where attached_to_doctype = "Leads" and attached_to_name = %s
    """,(lead,),as_dict=True)
    return data








