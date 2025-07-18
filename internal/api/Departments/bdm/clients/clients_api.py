import frappe
from collections import defaultdict

@frappe.whitelist()
def get_clients_for_user():
    user = frappe.session.user
    
    # Get all leads for the user with comprehensive fields
    leads = frappe.db.get_all(
        'Leads',
        filters={
            'leasing_status': 'Client',
            'assignedto': user
        },
        fields=[
            'name', 'name1', 'mobile_phone', 'primary_email', 'leasing_status',
             'assignedto', 'secondary_email', 'whatsapp_link_1', 'whatsapp_link_2'
        ]
    )
    
    if not leads:
        return []
    
    results = []
    for lead in leads:
        try:
            # Get the full lead document to access child tables for billing info
            lead_doc = frappe.get_doc('Leads', lead['name'])
            
            name = lead.get('name1') or ''
            initials = ''.join([part[0].upper() for part in name.split() if part])[:2]
            contact = lead.get('mobile_phone') or lead.get('primary_email') or ''
            
            # Calculate seats info from child table
            seats_count = 0
            total_seats_amount = 0
            if hasattr(lead_doc, 'item') and lead_doc.item:
                for item in lead_doc.item:
                    seats_count += item.get('qty', 0) or 0
                    total_seats_amount += item.get('amount', 0) or 0
            
            # Calculate amenities info from child table
            amenities_count = 0
            total_amenities_amount = 0
            if hasattr(lead_doc, 'amenity_recursion') and lead_doc.amenity_recursion:
                for amenity in lead_doc.amenity_recursion:
                    amenities_count += amenity.get('qty', 0) or 0
                    total_amenities_amount += amenity.get('amount', 0) or 0
            
            total_billed_items = seats_count + amenities_count
            total_amount = total_seats_amount + total_amenities_amount
            
            results.append({
                'id': lead['name'],
                'leadId': lead['name'],
                'name': lead.get('name1', ''),
                'contact': contact,
                'status': lead.get('leasing_status', ''),
                'initials': initials,
                'billedItemsCount': total_billed_items,
                'seatsCount': seats_count,
                'amenitiesCount': amenities_count,
                'totalAmount': total_amount,
                'totalSeatsAmount': total_seats_amount,
                'totalAmenitiesAmount': total_amenities_amount,
                'agreement': lead.get('agreement', ''),
                # Basic details
                'company': lead.get('company', ''),
                'assigned_to': lead.get('assignedto', ''),
                'managed_by': lead.get('managed_by', ''),
                'primary_email': lead.get('primary_email', ''),
                'secondary_email': lead.get('secondary_email', ''),
                'mobile_phone': lead.get('mobile_phone', ''),
                'alternative_number': lead.get('alternative_number', ''),
                'whatsapp_link_1': lead.get('whatsapp_link_1', ''),
                'whatsapp_link_2': lead.get('whatsapp_link_2', ''),
                'lead_title': lead.get('lead_title', ''),
                'building': lead.get('building', ''),
                'floor': lead.get('floor', ''),
                'nearby': lead.get('nearby', '')
            })
        except Exception as e:
            # Log error and continue with other leads
            print(f"Error processing lead {lead['name']}: {str(e)}")
            continue
    
    return results

@frappe.whitelist()
def get_client_details(lead_id):
    """
    Fetch detailed information for a specific client by lead ID
    """
    try:
        # Check if lead exists
        if not frappe.db.exists('Leads', lead_id):
            return {
                'success': False,
                'message': f'Lead {lead_id} not found'
            }
        
        # Get the lead document with all fields
        lead_doc = frappe.get_doc('Leads', lead_id)
        
        # Basic client info
        name = lead_doc.get('name1') or ''
        initials = ''.join([part[0].upper() for part in name.split() if part])[:2]
        contact = lead_doc.get('mobile_phone') or lead_doc.get('primary_email') or ''
        
        # Get seats recursion (item table) with full details
        seats_recursion = []
        if hasattr(lead_doc, 'item') and lead_doc.item:
            for item in lead_doc.item:
                seats_recursion.append({
                    'id': item.name,
                    'type': 'Seat',
                    'option': item.item_code or '',
                    'quantity': item.qty or 0,
                    'note': item.sales_description or '',
                    'rate': item.rate or 0,
                    'amount': item.amount or 0,
                    'start_date': item.start_date,
                    'stop_date': item.stop_date,
                    'rollout_status': item.rollout_status,
                    'floor': getattr(item, 'floor', ''),
                    'novel_billing_entity': getattr(item, 'novel_billing_entity', ''),
                    'billing_period': getattr(item, 'billing_period', ''),
                    'deposit_amt': getattr(item, 'deposit_amt', 0),
                    'deposit_months': getattr(item, 'deposit_months', 0)
                })
        
        # Get amenity recursion with full details
        amenity_recursion = []
        if hasattr(lead_doc, 'amenity_recursion') and lead_doc.amenity_recursion:
            for amenity in lead_doc.amenity_recursion:
                amenity_recursion.append({
                    'id': amenity.name,
                    'type': 'Amenity',
                    'option': amenity.item_code or '',
                    'quantity': amenity.qty or 0,
                    'note': amenity.sales_description or '',
                    'rate': amenity.rate or 0,
                    'amount': amenity.amount or 0,
                    'start_date': amenity.start_date,
                    'stop_date': amenity.stop_date,
                    'rollout_status': amenity.rollout_status,
                    'floor': getattr(amenity, 'floor', ''),
                    'novel_billing_entity': getattr(amenity, 'novel_billing_entity', ''),
                    'billing_period': getattr(amenity, 'billing_period', ''),
                    'deposit_amt': getattr(amenity, 'deposit_amt', 0),
                    'deposit_months': getattr(amenity, 'deposit_months', 0)
                })
        
        # Calculate totals
        total_seats_amount = sum(item['amount'] for item in seats_recursion)
        total_amenities_amount = sum(amenity['amount'] for amenity in amenity_recursion)
        total_amount = total_seats_amount + total_amenities_amount
        
        # Additional lead details
        lead_details = {
            'id': lead_id,
            'leadId': lead_id,
            'name': name,
            'contact': contact,
            'status': lead_doc.get('leasing_status', ''),
            'initials': initials,
            'company': lead_doc.get('company', ''),
            'lead_title': lead_doc.get('lead_title', ''),
            'building': lead_doc.get('building', ''),
            'floor': lead_doc.get('floor', ''),
            'nearby': lead_doc.get('nearby', ''),
            'agreement': lead_doc.get('agreement', ''),
            'seatsRecursion': seats_recursion,
            'amenityRecursion': amenity_recursion,
            'totalSeatsAmount': total_seats_amount,
            'totalAmenitiesAmount': total_amenities_amount,
            'totalAmount': total_amount,
            'seatsCount': len(seats_recursion),
            'amenitiesCount': len(amenity_recursion),
            'totalBilledItems': len(seats_recursion) + len(amenity_recursion),
            # Basic details
            'assigned_to': lead_doc.get('assignedto', ''),
            'managed_by': lead_doc.get('managed_by', ''),
            'primary_email': lead_doc.get('primary_email', ''),
            'secondary_email': lead_doc.get('secondary_email', ''),
            'mobile_phone': lead_doc.get('mobile_phone', ''),
            'alternative_number': lead_doc.get('alternative_number', ''),
            'whatsapp_link_1': lead_doc.get('whatsapp_link_1', ''),
            'whatsapp_link_2': lead_doc.get('whatsapp_link_2', ''),
            'email': lead_doc.get('primary_email', '') or lead_doc.get('secondary_email', ''),
            'whatsapp_link': lead_doc.get('whatsapp_link_1', '') or lead_doc.get('whatsapp_link_2', '')
        }
        
        return {
            'success': True,
            'data': lead_details
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching client details: {str(e)}'
        }

@frappe.whitelist()
def get_seats_recursion(lead_id):
    """
    Returns seat (item) child table data for a given lead
    """
    if not frappe.db.exists('Leads', lead_id):
        return {'success': False, 'message': 'Lead not found'}

    try:
        lead_doc = frappe.get_doc('Leads', lead_id)

        seat_items = []
        for item in lead_doc.item:
            seat_items.append({
                'name': item.name,  # unique row ID
                'item_code': item.item_code,
                'sales_description': item.sales_description,
                'qty': item.qty,
                'rate': item.rate,
                'amount': item.amount,
                'start_date': item.start_date,
                'stop_date': item.stop_date,
                'rollout_status': item.rollout_status,
                'floor': getattr(item, 'floor', ''),
                'novel_billing_entity': getattr(item, 'novel_billing_entity', ''),
                'billing_period': getattr(item, 'billing_period', ''),
                'deposit_amt': getattr(item, 'deposit_amt', 0),
                'deposit_months': getattr(item, 'deposit_months', 0)
            })

        return {
            'success': True,
            'data': seat_items
        }

    except Exception as e:
        return {'success': False, 'message': str(e)}

@frappe.whitelist()
def get_client_attachments(lead_id):
    """
    Fetch attachments for a specific client/lead
    """
    try:
        # Check if lead exists
        if not frappe.db.exists('Leads', lead_id):
            return []
        
        # Get attachments from File doctype
        attachments = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Leads",
                "attached_to_name": lead_id
            },
            fields=["name", "file_name", "file_url", "is_private", "file_size", "content_hash"]
        )
        
        # Process attachments to include file type and formatted size
        processed_attachments = []
        for attachment in attachments:
            file_name = attachment.get('file_name', '')
            file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
            
            # Determine file type based on extension
            file_type = 'other'
            if file_extension in ['pdf']:
                file_type = 'pdf'
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
                file_type = 'image'
            elif file_extension in ['doc', 'docx']:
                file_type = 'document'
            elif file_extension in ['xls', 'xlsx']:
                file_type = 'spreadsheet'
            elif file_extension in ['txt', 'md']:
                file_type = 'text'
            
            # Format file size
            file_size = attachment.get('file_size', 0)
            formatted_size = format_file_size(file_size)
            
            processed_attachments.append({
                'id': attachment.get('name'),
                'file_name': file_name,
                'file_url': attachment.get('file_url'),
                'is_private': attachment.get('is_private', False),
                'file_type': file_type,
                'file_size': file_size,
                'formatted_size': formatted_size,
                'content_hash': attachment.get('content_hash')
            })
        
        return processed_attachments
        
    except Exception as e:
        print(f"Error fetching attachments for lead {lead_id}: {str(e)}")
        return []

def format_file_size(size_bytes):
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"



