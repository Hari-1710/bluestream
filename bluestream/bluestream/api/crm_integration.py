import frappe
import json

@frappe.whitelist(allow_guest=True)
def crm_api_integration():
    """Create a new Lead record from external CRM integration via JSON POST."""
    frappe.local.response['content_type'] = 'application/json'

    try:
        # --- Parse JSON body ---
        data = frappe.request.get_data(as_text=True)
        if not data:
            frappe.local.response['http_status_code'] = 400
            return {"status": "error", "message": "Request body is empty."}

        payload = json.loads(data)

        # --- Extract fields from JSON body ---
        lead_name = payload.get("lead_name")
        email = payload.get("email")
        phone = payload.get("phone")
        company_name = payload.get("company_name")
        campaign = payload.get("campaign")
        source = payload.get("source")
        lead_owner = payload.get("lead_owner")
        status = payload.get("status", "Open")
        comments = payload.get("comments")

        # --- Validate mandatory fields ---
        missing_fields = []
        if not lead_name:
            missing_fields.append("lead_name")
        if not email:
            missing_fields.append("email")
        # if not phone:
        #     missing_fields.append("phone")

        if missing_fields:
            frappe.local.response['http_status_code'] = 400
            return {
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}."
            }
        
        # --- Prevent duplicate leads ---
        # existing_by_email = frappe.db.exists("Lead", {"email_id": email})
         
        if phone:
            existing_by_phone = frappe.db.exists("Lead", {"phone": phone})

        # if existing_by_email or existing_by_phone:
        # if existing_by_email:
        #     frappe.local.response['http_status_code'] = 409  # HTTP 409 Conflict
        #     return {
        #         "status": "error",
        #         "message": "Lead already exists with the same email or phone number.",
        #         "existing_lead": existing_by_email or existing_by_phone
        #     }

        # --- Create new Lead ---
        lead_doc = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": lead_name,
            "email_id": email,
            "phone": phone,
            "company_name": company_name,
            "campaign_name": campaign,
            "source": source or "External API",
            "status": status,
            "lead_owner": lead_owner or frappe.session.user,
            "comments": comments or ""
        })

        lead_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # --- Success response ---
        frappe.local.response['http_status_code'] = 200
        return {
            "status": "success",
            "message": "New lead created successfully.",
            "lead_id": lead_doc.name,
            "data": {
                "lead_name": lead_doc.lead_name,
                "email": lead_doc.email_id,
                "phone": lead_doc.phone,
                "company_name": lead_doc.company_name,
                "campaign": lead_doc.campaign_name,
                "source": lead_doc.source,
                "status": lead_doc.status,
                "comments": getattr(lead_doc, "comments", "")
            }
        }

    except Exception as e:
        frappe.log_error(message=f"CRM API Integration Failed: {str(e)}", title="CRM API Error")
        frappe.local.response['http_status_code'] = 500
        return {
            "status": "error",
            "message": f"Failed to create lead: {str(e)}"
        }
