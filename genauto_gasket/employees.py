"""
Bulk import employees from eSSL biometric roster.
Source: /Users/vibhavaggarwal/Projects/Bhuvan/Devices/Biometric/eSSL-X2008_QJT3253600356/Employees.md
Maps PIN → Employee.attendance_device_id
"""
import frappe
from datetime import date

COMPANY = "Genauto Gasket Technologies LLP"
DEFAULT_JOINING_DATE = "2026-04-01"  # Fiscal year start; real DOJ to be updated per worker

# PIN → Name (from Employees.md)
EMPLOYEES = [
    (1, "Naresh Sir"),
    (2, "Pramod Kumar"),
    (3, "Bhola Girdhari"),
    (4, "Harvinder"),
    (5, "Govind Kumar"),
    (6, "Chandan Kumar"),
    (7, "Shivam Kumar Mishra"),
    (8, "Ajay Kumar"),
    (9, "Samarjeet"),
    (10, "Santosh Kumar"),
    (11, "Rohit"),
    (12, "Manish Pandey"),
    (13, "Dinesh"),
    (14, "Raju Yadav"),
    (15, "Vishal Kumar"),
    (16, "Pradeep Kumar"),
    (17, "Andeep Kumar"),
    (18, "Vijay Ram"),
    (19, "Ranjan Kumar"),
    (20, "Nitu Devi"),
    (21, "Rajeshvari Devi"),
    (22, "Prabhat Kumar"),
    (23, "Ravi"),
    (24, "Bhupendra"),
    (25, "Ashish"),
    (26, "Sahil"),
    (27, "Suraj Kumar"),
    (28, "Kush"),
    (29, "Rajnish Kumar"),
    (30, "Deepu"),
    (31, "Nandlal Patel"),
    (32, "Vishal Kumar"),
    (33, "Atul"),
    (34, "Munesh"),
    (35, "Sandeep"),
    (36, "Taiba Khatun"),
    (37, "Kadir"),
    (38, "Urmila Devi"),
    (39, "Jamuna Nath"),
    (40, "Aarti Barnwal"),
    (41, "Anjeet Kumar"),
    (42, "Ram Kumar"),
    (43, "Manjeet"),
    (44, "Jalpati Devi"),
    (45, "Radheshyam"),
    (46, "Avnish Singh"),
    (47, "Anil Kumar"),
    (48, "Rahul Kumar Ram"),
    (49, "Ranjan"),
    (50, "Mantu Kumar"),
    (51, "Pawan"),
    (52, "Monu Kumar"),
    (53, "Rahul Kumar"),
    (54, "Manish Kumar"),
    (55, "Surendra Kumar"),
    (56, "Raja"),
    (57, "Ram Milan"),
    (58, "Saurabh Yadav"),
    (59, "Dhiraj Kumar"),
    (60, "Shankar Sha"),
    (61, "Shiv Kumar"),
    (62, "Vikram Singh"),
    (63, "Sahil"),
    (64, "Jageshwar"),
    (65, "Ajit Kumar"),
    (66, "Sanjeet Kumar"),
    (67, "Kajal Devi"),
    (68, "Akahay"),
    (69, "Bijendra Singh"),
    (70, "Himanshu Pal"),
    (71, "Shalik Kumar"),
    (72, "Ankush Chawla"),
    (73, "Pooja"),
    (74, "Kuldeep Driver"),
    (75, "Kewal Krishan"),
    (76, "Amar Ahirwar"),
    (77, "Kailash Chander"),
    (78, "Archana Devi"),
    (79, "Arpit Tiwari"),
    (80, "Vinod Ahirwal"),
    (81, "Rahul Bhar"),
    (82, "Ladli Kumari"),
    (83, "Kiran"),
    (84, "Bhawana"),
    (85, "Vibhav"),
    (86, "Bhuvnesh"),
]

# Gender heuristic — based on common Indian name patterns
FEMALE_MARKERS = ("Devi", "Kumari", "Khatun", "Nath", "Barnwal", "Pooja", "Bhawana", "Kiran", "Ladli", "Archana")
FEMALE_SPECIFIC = {20, 21, 36, 38, 39, 40, 44, 67, 73, 78, 82, 83, 84}  # explicitly female from list


def _gender_for(pin: int, name: str) -> str:
    if pin in FEMALE_SPECIFIC:
        return "Female"
    for marker in FEMALE_MARKERS:
        if marker in name:
            return "Female"
    return "Male"


def import_employees():
    print(f"Importing {len(EMPLOYEES)} employees…")
    created = skipped = 0
    for pin, name in EMPLOYEES:
        # Idempotency: if any employee already has this attendance_device_id, skip
        existing = frappe.db.get_value("Employee", {"attendance_device_id": str(pin)}, "name")
        if existing:
            skipped += 1
            continue

        emp = frappe.new_doc("Employee")
        # Split name into first/middle/last
        parts = name.split()
        emp.first_name = parts[0]
        if len(parts) > 2:
            emp.middle_name = " ".join(parts[1:-1])
            emp.last_name = parts[-1]
        elif len(parts) == 2:
            emp.last_name = parts[1]
        emp.employee_name = name
        emp.attendance_device_id = str(pin)
        emp.gender = _gender_for(pin, name)
        emp.date_of_joining = DEFAULT_JOINING_DATE
        emp.date_of_birth = "1990-01-01"  # placeholder — to be updated
        emp.company = COMPANY
        emp.status = "Active"
        emp.language_preference = "hi"

        try:
            emp.insert(ignore_permissions=True)
            created += 1
            print(f"  [+] PIN {pin}: {name} → {emp.name}")
        except Exception as e:
            print(f"  [!] PIN {pin}: {name} FAILED — {e}")

    frappe.db.commit()
    print(f"\n✓ Created: {created}  |  Skipped: {skipped}")


def generate_bridge_api_key():
    """Create or reuse a service user + API key for the ZKTeco bridge."""
    user_email = "zkteco-bridge@genautoindia.com"
    if frappe.db.exists("User", user_email):
        user = frappe.get_doc("User", user_email)
    else:
        user = frappe.new_doc("User")
        user.email = user_email
        user.first_name = "ZKTeco"
        user.last_name = "Bridge"
        user.enabled = 1
        user.user_type = "System User"
        user.send_welcome_email = 0
        user.append("roles", {"role": "HR User"})
        user.insert(ignore_permissions=True)
        print(f"  [+] Created service user: {user_email}")

    # Regenerate API secret
    import secrets as _secrets
    api_secret = _secrets.token_urlsafe(32)
    user.api_key = user.api_key or frappe.generate_hash(length=15)
    user.api_secret = api_secret
    user.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"\nAPI Credentials for /etc/systemd/system/zkteco-bridge.service:")
    print(f"  API_KEY={user.api_key}")
    print(f"  API_SECRET={api_secret}")
    return user.api_key, api_secret


def setup_all():
    import_employees()
    print()
    key, secret = generate_bridge_api_key()
    print("\nDone.")
    return {"api_key": key, "api_secret": secret}
