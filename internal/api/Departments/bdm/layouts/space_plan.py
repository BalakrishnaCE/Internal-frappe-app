import frappe
import json

@frappe.whitelist()
def save_space_plan_requirement(
    lead_id=None,
    additional_comments=None,
    location=None,
    floor=None,
    nearby_place=None,
    quick_items_json=None
):
    """
    Add requirement to existing Space Plan for this lead,
    or create a new Space Plan if none exists.
    Always update status to 'Required' when adding new requirement.
    """
    if not lead_id:
        raise Exception("lead_id is required and was not provided.")

    quick_items = json.loads(quick_items_json or "[]")

    # Find existing Space Plan for this lead
    existing_docs = frappe.get_list(
        "Space Plan",
        filters={"lead_id": lead_id},
        fields=["name"]
    )

    if existing_docs:
        docname = existing_docs[0].name
        doc = frappe.get_doc("Space Plan", docname)

        doc.additional_comments = additional_comments
        doc.status = "Required"  # ✅ always force status to 'required'

        # Add new location row
        doc.append("location", {
            "location": location,
            "floor": floor,
            "attachment": "dummy.pdf",
            "comment": nearby_place or ""
        })

        # Add quick items
        for item in quick_items:
            doc.append("item_table", {
                "category": item.get("category") or "",
                "item": item.get("item") or "",
                "required": item.get("required") or 0,
                "quantity": item.get("quantity") or 1,
                "comment": item.get("comment") or ""
            })

        doc.save(ignore_permissions=True)
        frappe.db.commit()

        return {"message": "Requirement added to existing Space Plan", "docname": doc.name}

    else:
        # Create new Space Plan doc
        doc = frappe.get_doc({
            "doctype": "Space Plan",
            "lead_id": lead_id,
            "additional_comments": additional_comments,
            "status": "Required"  # ✅ new doc always starts as 'required'
        })

        # Add location row
        doc.append("location", {
            "location": location,
            "floor": floor,
            "attachment": "dummy.pdf",
            "comment": nearby_place or ""
        })

        # Add quick items
        for item in quick_items:
            doc.append("item_table", {
                 "category": item.get("category") or "",
                "item": item.get("item") or "",
                "required": item.get("required") or 0,
                "quantity": item.get("quantity") or 1,
                "comment": item.get("comment") or ""
            })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"message": "New Space Plan created successfully", "docname": doc.name}

@frappe.whitelist(allow_guest=False)
def get_space_plan_pdfs(lead_id):
    """
    Fetch PDFs from Space Plan Detail doctype's child tables.
    Latest PDFs: from "old" child table where approved = 1
    Previous PDFs: from "new" child table (all files)
    """
    try:
        frappe.log_error(f"🔍 Starting get_space_plan_pdfs for lead_id: {lead_id}")
        
        # Try different approaches to find Space Plan Detail documents
        space_plan_details = []
        
        # Approach 1: Try with lead_id filter
        try:
            space_plan_details = frappe.get_list(
                "Space Plan detail",
                filters={"lead_id": lead_id},
                fields=["name"]
            )
            frappe.log_error(f"📋 Approach 1: Found {len(space_plan_details)} Space Plan detail documents with lead_id filter")
        except Exception as e:
            frappe.log_error(f"❌ Approach 1 failed: {str(e)}")
        
        # Approach 2: If no results, try without lead_id filter (get all)
        if not space_plan_details:
            try:
                space_plan_details = frappe.get_list(
                    "Space Plan detail",
                    fields=["name", "parent", "lead_id"] if "lead_id" in frappe.get_meta("Space Plan detail").fields else ["name", "parent"]
                )
                frappe.log_error(f"📋 Approach 2: Found {len(space_plan_details)} total Space Plan detail documents")
                # Filter by lead_id if the field exists
                if "lead_id" in frappe.get_meta("Space Plan detail").fields:
                    space_plan_details = [doc for doc in space_plan_details if doc.get("lead_id") == lead_id]
                    frappe.log_error(f"📋 After lead_id filtering: {len(space_plan_details)} documents")
            except Exception as e:
                frappe.log_error(f"❌ Approach 2 failed: {str(e)}")
        
        # Approach 3: Try to find by parent relationship (if Space Plan Detail is a child table of Space Plan)
        if not space_plan_details:
            try:
                # Get the Space Plan document first
                space_plan_docs = frappe.get_list(
                    "Space Plan",
                    filters={"lead_id": lead_id},
                    fields=["name"]
                )
                if space_plan_docs:
                    space_plan_name = space_plan_docs[0].name
                    space_plan_details = frappe.get_list(
                        "Space Plan detail",
                        filters={"parent": space_plan_name},
                        fields=["name"]
                    )
                    frappe.log_error(f"📋 Approach 3: Found {len(space_plan_details)} Space Plan detail documents as child of Space Plan {space_plan_name}")
            except Exception as e:
                frappe.log_error(f"❌ Approach 3 failed: {str(e)}")

        frappe.log_error(f"📋 Final Space Plan detail documents: {space_plan_details}")

        latest_pdfs = []
        previous_pdfs = []

        for detail_doc in space_plan_details:
            frappe.log_error(f"🔍 Processing Space Plan detail: {detail_doc.name}")
            doc = frappe.get_doc("Space Plan detail", detail_doc.name)
            
            # Debug: Check what attributes the doc has
            doc_attrs = [attr for attr in dir(doc) if not attr.startswith('_')]
            frappe.log_error(f"🔍 Doc attributes: {doc_attrs}")
            
            # Try different child table names
            child_table_names = ['old', 'new', 'latest_files', 'previous_files', 'files', 'attachments']
            
            for table_name in child_table_names:
                if hasattr(doc, table_name) and getattr(doc, table_name):
                    frappe.log_error(f"🔍 Found child table: {table_name} with {len(getattr(doc, table_name))} items")
                    
                    # Check if this is the "old" table (for latest PDFs)
                    if table_name in ['old', 'latest_files']:
                        for item in getattr(doc, table_name):
                            frappe.log_error(f"🔍 {table_name} item: name={item.name}, approved={getattr(item, 'approved', 'N/A')}, attachment={getattr(item, 'attachment', 'N/A')}")
                            if hasattr(item, 'approved') and hasattr(item, 'attachment'):
                                if item.approved == 1 and item.attachment:
                                    latest_pdfs.append({
                                        "name": item.name,
                                        "attachment": item.attachment,
                                        "comment": getattr(item, 'comment', '') or "",
                                        "location": getattr(item, 'location', '') or "",
                                        "floor": getattr(item, 'floor', '') or ""
                                    })
                                    frappe.log_error(f"✅ Added to latest_pdfs: {item.attachment}")
                    
                    # Check if this is the "new" table (for previous PDFs)
                    elif table_name in ['new', 'previous_files']:
                        for item in getattr(doc, table_name):
                            frappe.log_error(f"🔍 {table_name} item: name={item.name}, approved={getattr(item, 'approved', 'N/A')}, attachment={getattr(item, 'attachment', 'N/A')}")
                            if hasattr(item, 'attachment') and item.attachment:
                                previous_pdfs.append({
                                    "name": item.name,
                                    "attachment": item.attachment,
                                    "comment": getattr(item, 'comment', '') or "",
                                    "location": getattr(item, 'location', '') or "",
                                    "floor": getattr(item, 'floor', '') or "",
                                    "approved": getattr(item, 'approved', 0) or 0
                                })
                                frappe.log_error(f"✅ Added to previous_pdfs: {item.attachment}")

        frappe.log_error(f"📊 Final results: latest_pdfs={len(latest_pdfs)}, previous_pdfs={len(previous_pdfs)}")
        frappe.log_error(f"📊 Latest PDFs: {latest_pdfs}")
        frappe.log_error(f"📊 Previous PDFs: {previous_pdfs}")

        return {
            "latest_pdfs": latest_pdfs,
            "previous_pdfs": previous_pdfs
        }

    except Exception as e:
        frappe.log_error(f"❌ Error in get_space_plan_pdfs: {str(e)}")
        frappe.log_error(f"❌ Error traceback: {frappe.get_traceback()}")
        return {
            "latest_pdfs": [],
            "previous_pdfs": []
        }


@frappe.whitelist(allow_guest=False)
def get_space_plan_by_lead(lead_id=None):
    """
    Fetch existing Space Plan by lead_id.
    Return selected fields only, including status.
    Only fetch items where required = 1 (checked).
    Now also includes PDFs from Space Plan Detail doctype.
    """
    try:
        if not lead_id:
            raise Exception("lead_id is required and was not provided.")

        existing_docs = frappe.get_list(
            "Space Plan",
            filters={"lead_id": lead_id},
            fields=["name", "additional_comments", "status"]
        )

        if not existing_docs:
            return {"exists": False}

        docname = existing_docs[0].name
        doc = frappe.get_doc("Space Plan", docname)

        # Build locations list
        locations = [{
            "location": loc.location or "",
            "floor": loc.floor or "",
            "attachment": loc.attachment or "",
            "comment": loc.comment or ""
        } for loc in doc.location]

        # Build items list - ONLY where required = 1
        items = []
        for item in doc.item_table:
            if item.required == 1:
                item_data = {
                    "category": item.category or "",
                    "item": item.item or "",
                    "required": item.required or 0,
                    "quantity": item.quantity or 1,
                    "comment": item.comment or ""
                }
                items.append(item_data)

        # Get PDFs from Space Plan Detail
        pdfs = get_space_plan_pdfs(lead_id)

        data = {
            "name": doc.name,
            "additional_comments": doc.additional_comments or "",
            "status": doc.status or "",
            "locations": locations,
            "items": items,
            "latest_pdfs": pdfs["latest_pdfs"],
            "previous_pdfs": pdfs["previous_pdfs"]
        }

        return {"exists": True, "data": data}

    except Exception as e:
        frappe.log_error(f"Error in get_space_plan_by_lead: {str(e)}")
        return {"error": str(e)}
    


@frappe.whitelist()
def fetch_space_paln_details_data():
    lead = frappe.form_dict.get("lead")
    data = frappe.db.sql("""
        select c.name1,c.approved, c.attachment
        from `tabSpace Plan` p
        join `tabSpace Plan detail` c on p.name = c.parent
        where p.name = %s
    """,(lead,),as_dict=True)
    return data
