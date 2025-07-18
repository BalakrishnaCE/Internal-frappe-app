import frappe

def get_seats_list():
    """Get list of seats from the 'Leads Items for number of seats' doctype"""
    try:
        # Get all documents from the doctype
        seats_docs = frappe.get_all("Leads Items for number of seats", fields=["name"])
        seats_list = []
        
        for seat_doc in seats_docs:
            seats_list.append(seat_doc)
        
        return seats_list
    except Exception as e:
        frappe.log_error(f"Error fetching seats list: {str(e)}")
        return []

def get_amenities_list():
    """Get list of amenities from the 'Leads item for Amenities' doctype"""
    try:
        # Get all documents from the doctype
        amenities_docs = frappe.get_all("Leads item for Amenities", fields=["name"])
        amenities_list = []
        
        for amenity_doc in amenities_docs:
            amenities_list.append(amenity_doc)
        
        return amenities_list
    except Exception as e:
        frappe.log_error(f"Error fetching amenities list: {str(e)}")
        return []

@frappe.whitelist()
def get_seats_list_api():
    """API endpoint to get seats list"""
    try:
        seats = get_seats_list()
        return {
            "status": "success",
            "message": seats
        }
    except Exception as e:
        frappe.log_error(f"API Error in get_seats_list_api: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_amenities_list_api():
    """API endpoint to get amenities list"""
    try:
        amenities = get_amenities_list()
        return {
            "status": "success",
            "message": amenities
        }
    except Exception as e:
        frappe.log_error(f"API Error in get_amenities_list_api: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    seats = get_seats_list()
    amenities = get_amenities_list()
    print("Seats List:", seats)
    print("Amenities List:", amenities)

if __name__ == "__main__":
    main()