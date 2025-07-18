import frappe

@frappe.whitelist()
def loginUser_roles(loginUser):
    try:
        result = []

        # 1. Check if user is a regular user in any department
        user_children = frappe.get_all(
            "User Child",
            filters={"user_link": loginUser, "parentfield": "user"},
            fields=["parent"]
        )
        parent_names = [uc["parent"] for uc in user_children]
        if parent_names:
            roles = frappe.get_all(
                "Internal App Role",
                filters={"name": ["in", parent_names]},
                fields=["name", "department"]
            )
            for role in roles:
                result.append({
                    "department": role["department"],
                    "role_type": "user"
                })

        # 2. Check if user is a TL/Executive in any department (tls table)
        tl_children = frappe.get_all(
            "User Child",
            filters={"user_link": loginUser, "parentfield": "tls"},
            fields=["parent"]
        )
        tl_parent_names = [tc["parent"] for tc in tl_children]
        if tl_parent_names:
            tl_roles = frappe.get_all(
                "Internal App Role",
                filters={"name": ["in", tl_parent_names]},
                fields=["name", "department"]
            )
            for role in tl_roles:
                result.append({
                    "department": role["department"],
                    "role_type": "tl"
                })

        if not result:
            return {
                "error": True,
                "message": f"No department or role found for user: {loginUser}"
            }
        return {
            "error": False,
            "roles": result
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "loginUser_roles Error")
        return {
            "error": True,
            "message": f"An error occurred: {str(e)}"
        }
    