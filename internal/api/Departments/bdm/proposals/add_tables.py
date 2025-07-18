import frappe
import json
from frappe.utils import now_datetime
from frappe import _

@frappe.whitelist()
def get_details(lead_id="LEADID00286951"):
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
        
        # Get the lead document
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
            'company_name': lead_doc.get('company_name', ''),
            'lead_title': lead_doc.get('lead_title', ''),
            'building': lead_doc.get('building', ''),
            'floor': lead_doc.get('floor', ''),
            'nearby': lead_doc.get('nearby', ''),
            'agreement': '',
            'seatsRecursion': seats_recursion,
            'amenityRecursion': amenity_recursion,
            'totalSeatsAmount': total_seats_amount,
            'totalAmenitiesAmount': total_amenities_amount,
            'totalAmount': total_amount,
            'seatsCount': len(seats_recursion),
            'amenitiesCount': len(amenity_recursion),
            'totalBilledItems': len(seats_recursion) + len(amenity_recursion)
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
@frappe.whitelist(allow_guest=True)
def get_lead_summary(lead_id="LEADID00286951"):
    """
    Get a summary of lead data for quick overview
    
    Returns:
        dict: Summary of lead data
    """
    try:
        lead_data = get_details(lead_id)
        if not lead_data.get('success'):
            return {
                'success': False,
                'message': lead_data.get('message', 'Failed to fetch lead details')
            }
        lead_data = lead_data.get('data', {})
        
        summary = {
            "lead_title": lead_data.get("lead_title"),
            "total_items": len(lead_data.get("seatsRecursion", [])) + len(lead_data.get("amenityRecursion", [])),
            "seats_count": len(lead_data.get("seatsRecursion", [])),
            "amenities_count": len(lead_data.get("amenityRecursion", [])),
            "total_amount": lead_data.get("totalAmount", 0),
            "seats_total": lead_data.get("totalSeatsAmount", 0),
            "amenities_total": lead_data.get("totalAmenitiesAmount", 0)
        }
        
        return summary
        
    except Exception as e:
        frappe.log_error(f"Error in get_lead_summary: {str(e)}", "Lead Summary API Error")
        frappe.throw(_("Failed to fetch lead summary: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def add_tables(lead_id):
    """
    Main function to handle add_tables API requests
    """
    table_data = get_details("LEADID00286951")
    return {"status": "success", "data": table_data}

@frappe.whitelist(allow_guest=True)
def download_lead_data(lead_id, format_type='json'):
    """
    Download lead data in specified format
    
    Args:
        lead_id (str): The lead ID
        format_type (str): 'json', 'csv', or 'summary'
    
    Returns:
        dict: Formatted data for download
    """
    try:
        # Add debugging
        frappe.logger().info(f"Download request for lead_id: {lead_id}, format: {format_type}")
        
        # Validate lead_id
        if not lead_id:
            return {
                'success': False,
                'message': 'Lead ID is required'
            }
        if format_type == 'summary':
            data = get_lead_summary(lead_id)
            return {
                'success': True,
                'data': data,
                'format': 'summary'
            }
        else:
            # Get full details
            result = get_details(lead_id)
            if not result.get('success'):
                return result
            
            data = result.get('data', {})
            
            if format_type == 'json':
                return {
                    'success': True,
                    'data': data,
                    'format': 'json'
                }
            elif format_type == 'csv':
                # Convert to CSV format
                csv_data = []
                
                # Add header
                csv_data.append(['Type', 'Item Code', 'Quantity', 'Rate', 'Amount', 'Start Date', 'Stop Date', 'Floor', 'Billing Period'])
                
                # Add seats
                for seat in data.get('seatsRecursion', []):
                    csv_data.append([
                        'Seat',
                        seat.get('option', ''),
                        seat.get('quantity', 0),
                        seat.get('rate', 0),
                        seat.get('amount', 0),
                        seat.get('start_date', ''),
                        seat.get('stop_date', ''),
                        seat.get('floor', ''),
                        seat.get('billing_period', '')
                    ])
                
                # Add amenities
                for amenity in data.get('amenityRecursion', []):
                    csv_data.append([
                        'Amenity',
                        amenity.get('option', ''),
                        amenity.get('quantity', 0),
                        amenity.get('rate', 0),
                        amenity.get('amount', 0),
                        amenity.get('start_date', ''),
                        amenity.get('stop_date', ''),
                        amenity.get('floor', ''),
                        amenity.get('billing_period', '')
                    ])
                
                return {
                    'success': True,
                    'data': csv_data,
                    'format': 'csv'
                }
            else:
                return {
                    'success': False,
                    'message': f'Unsupported format: {format_type}'
                }
                
    except Exception as e:
        return {
            'success': False,
            'message': f'Error downloading lead data: {str(e)}'
        }

@frappe.whitelist(allow_guest=True)
def create_download_file(lead_id, format_type='json'):
    """
    Create a downloadable file for the lead data
    
    Args:
        lead_id (str): The lead ID
        format_type (str): 'json', 'csv', or 'summary'
    
    Returns:
        dict: File information for download
    """
    try:
        # Get the data
        result = download_lead_data(lead_id, format_type)
        
        if not result.get('success'):
            return result
        
        data = result.get('data', {})
        
        # Create file name
        timestamp = now_datetime().strftime('%Y%m%d_%H%M%S')
        filename = f"lead_{lead_id}_{format_type}_{timestamp}"
        
        if format_type == 'json':
            filename += '.json'
            file_content = json.dumps(data, indent=2, default=str)
        elif format_type == 'csv':
            filename += '.csv'
            # Convert CSV array to string
            csv_content = []
            for row in data:
                csv_content.append(','.join([f'"{str(cell)}"' for cell in row]))
            file_content = '\n'.join(csv_content)
        else:
            filename += '.txt'
            file_content = json.dumps(data, indent=2, default=str)
        
        
        return {
            'success': True,
            'file_url': file_content,
            'file_name': filename,
            'format': format_type
        }
        
    except Exception as e:
        frappe.logger().error(f"Error creating download file: {str(e)}")
        return {
            'success': False,
            'message': f'Error creating download file: {str(e)}'
        }
