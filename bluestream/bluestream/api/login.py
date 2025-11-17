import frappe
import json
import secrets
from frappe.auth import LoginManager
from frappe.utils.password import update_password 
 
@frappe.whitelist(allow_guest=True)
def user_login():
    """
    Handles customer signin by validating user credentials.
    """
 
    form_data = json.loads(frappe.request.get_data())
 
    login_manager = LoginManager()
    login_manager.authenticate(form_data.get("email"), form_data.get("password"))
    login_manager.post_login()
 
    if frappe.response["message"] == "Logged In":
        user = login_manager.user
        user_details = frappe.get_doc("User", user)
        
        frappe.response["user_details"] = {
            "api_key": user_details.api_key,
            "api_secret": user_details.get_password("api_secret"),
            "api_token": f"token {user_details.api_key}:{user_details.get_password('api_secret')}"
        }

    else:
        return False
 

@frappe.whitelist(allow_guest=True)
def create_user():
    form_data = json.loads(frappe.request.get_data())

    email = form_data.get("email")
    first_name = form_data.get("first_name")
    password = form_data.get("password")

    if not email or not first_name or not password:
        return {"error": "Email, First Name, and Password are required."}

    if frappe.db.exists("User", email):
        return {"error": "A user with this email already exists."}

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "send_welcome_email": 0,
        "user_type": "Website User",
        "enabled": 1
    })
    user.insert(ignore_permissions=True)

    update_password(user.name, password)

    # Generate and store API credentials
    api_key = frappe.generate_hash(length=15)
    api_secret = frappe.generate_hash(length=15)

    user.api_key = api_key
    user.api_secret = api_secret
    user.save(ignore_permissions=True)

    # Build token: api_key + ":" + api_secret
    api_token = f"token {api_key}:{api_secret}"

    return {
        "message": "User created successfully",
        "user_details": {
            "email": email,
            "api_key": api_key,
            "api_secret": api_secret,        # ← NOW REAL SECRET
            "api_token": api_token            # ← NEW FIELD ADDED
        }
    }

@frappe.whitelist(allow_guest=True)
def forgot_password():
    # Get the form data from the request
    form_data = json.loads(frappe.request.get_data())
 
    if not frappe.db.exists("User", form_data.get("email")):
        return {"error": "User with this email does not exist"}
 
    if send_login_link(form_data.get("email")):
        return {"data": "Password reset link sent to your email."}

def before_save_user(user, method=None):
    """
    Doc event hook: set a random api_secret for User before save.
    To activate, add to your hooks.py:
      doc_events = {"User": {"before_save": "bluestream.bluestream.api.login.before_save_user"}}
    """
    if not user.get("api_secret"):
        user.api_key = frappe.generate_hash(length=15)
        user.api_secret = frappe.generate_hash(length=15)
        # The document will be saved after this hook runs. Avoid calling user.save() here to prevent recursion.
        # If you explicitly want to persist immediately (not recommended), uncomment:
        # user.save(ignore_permissions=True)