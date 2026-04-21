"""
Genauto Gasket — Custom DocTypes + Fields bootstrap
Run: bench --site erp.genautoindia.com execute genauto_gasket.bootstrap.setup_all
"""
import frappe
from frappe.model.document import Document


MODULE = "Genauto Gasket"


def _create_doctype(name: str, fields: list, istable: int = 0, autoname: str | None = None,
                    title_field: str | None = None, search_fields: str | None = None,
                    naming_rule: str | None = None, is_submittable: int = 0,
                    track_changes: int = 1, quick_entry: int = 1) -> None:
    """Idempotent DocType creator that writes to app (custom=0)."""
    if frappe.db.exists("DocType", name):
        print(f"  [=] DocType exists: {name}")
        return

    dt = frappe.new_doc("DocType")
    dt.name = name
    dt.module = MODULE
    dt.custom = 0
    dt.istable = istable
    dt.is_submittable = is_submittable
    dt.track_changes = track_changes
    dt.quick_entry = quick_entry
    dt.allow_import = 0 if istable else 1
    if autoname:
        dt.autoname = autoname
    if title_field:
        dt.title_field = title_field
    if search_fields:
        dt.search_fields = search_fields
    if naming_rule:
        dt.naming_rule = naming_rule

    for f in fields:
        dt.append("fields", f)

    if not istable:
        dt.append("permissions", {
            "role": "System Manager",
            "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1,
            "export": 1, "import": 1, "share": 1, "print": 1, "email": 1,
        })
        role = ("Item Manager" if name in ("Die Master", "Frame Master", "Vehicle Application")
                else "Stock Manager" if "Delivery" in name
                else "HR Manager" if "Shift" in name or "Panic" in name
                else "Manufacturing Manager")
        dt.append("permissions", {
            "role": role,
            "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1,
            "export": 1, "share": 1, "print": 1, "email": 1,
        })

    dt.insert(ignore_permissions=True)
    print(f"  [+] Created DocType: {name}")


def create_vehicle_application():
    fields = [
        {"fieldname": "section_primary", "fieldtype": "Section Break", "label": "Vehicle"},
        {"fieldname": "vehicle_brand", "fieldtype": "Select", "label": "Brand", "reqd": 1,
         "options": "\nHONDA\nBAJAJ\nTVS\nYAMAHA\nSUZUKI\nROYAL ENFIELD\nHERO\nMAHINDRA\nMARUTI\nTATA\nASHOK LEYLAND\nOTHER"},
        {"fieldname": "vehicle_model", "fieldtype": "Data", "label": "Model", "reqd": 1, "in_list_view": 1},
        {"fieldname": "engine_type", "fieldtype": "Data", "label": "Engine Type"},
        {"fieldname": "col_break_1", "fieldtype": "Column Break"},
        {"fieldname": "year_from", "fieldtype": "Int", "label": "Year From"},
        {"fieldname": "year_to", "fieldtype": "Int", "label": "Year To"},
        {"fieldname": "oem_part_number", "fieldtype": "Data", "label": "OEM Part Number", "in_list_view": 1},
        {"fieldname": "section_item", "fieldtype": "Section Break", "label": "Gasket Item"},
        {"fieldname": "item_code", "fieldtype": "Link", "label": "Gasket Item", "options": "Item", "reqd": 1, "in_list_view": 1},
        {"fieldname": "col_break_2", "fieldtype": "Column Break"},
        {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"},
        {"fieldname": "section_competitors", "fieldtype": "Section Break", "label": "Competitor Cross-References",
         "collapsible": 1},
        {"fieldname": "competitor_refs", "fieldtype": "JSON", "label": "Competitor Part Numbers",
         "description": 'JSON: {"Victor":"V-123","Elring":"E-456","Payen":"BA123"}'},
    ]
    _create_doctype("Vehicle Application", fields,
                    title_field="vehicle_model",
                    search_fields="vehicle_brand,vehicle_model,oem_part_number")


def create_die_master():
    fields = [
        {"fieldname": "section_main", "fieldtype": "Section Break", "label": "Identification"},
        {"fieldname": "die_code", "fieldtype": "Data", "label": "Die Code", "reqd": 1, "unique": 1, "in_list_view": 1, "bold": 1},
        {"fieldname": "die_name", "fieldtype": "Data", "label": "Die Name", "reqd": 1, "in_list_view": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status", "in_list_view": 1,
         "options": "Active\nInactive\nRetired\nUnder Repair", "default": "Active"},
        {"fieldname": "criticality", "fieldtype": "Select", "label": "Criticality",
         "options": "A\nB\nC", "default": "B"},
        {"fieldname": "section_location", "fieldtype": "Section Break", "label": "Tooling Details"},
        {"fieldname": "tooling_type", "fieldtype": "Select", "label": "Type",
         "options": "PUNCH\nBLANKING\nFORMING\nDRAWING\nEMBOSSING\nCOMPOSITE\nPROGRESSIVE\nCOMPOUND"},
        {"fieldname": "tonnage_required", "fieldtype": "Float", "label": "Tonnage Required"},
        {"fieldname": "strokes_per_minute", "fieldtype": "Int", "label": "Strokes/Minute"},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "storage_location", "fieldtype": "Data", "label": "Storage Location"},
        {"fieldname": "current_machine", "fieldtype": "Link", "label": "Currently On Machine", "options": "Workstation"},
        {"fieldname": "section_lifecycle", "fieldtype": "Section Break", "label": "Lifecycle", "collapsible": 1},
        {"fieldname": "manufactured_on", "fieldtype": "Date", "label": "Manufactured On"},
        {"fieldname": "manufacturer", "fieldtype": "Data", "label": "Tooling Manufacturer"},
        {"fieldname": "cost", "fieldtype": "Currency", "label": "Tooling Cost"},
        {"fieldname": "col_3", "fieldtype": "Column Break"},
        {"fieldname": "stroke_counter", "fieldtype": "Int", "label": "Stroke Counter", "default": 0},
        {"fieldname": "design_life_strokes", "fieldtype": "Int", "label": "Design Life (strokes)"},
        {"fieldname": "last_maintenance", "fieldtype": "Date", "label": "Last Maintenance"},
        {"fieldname": "section_notes", "fieldtype": "Section Break", "collapsible": 1},
        {"fieldname": "notes", "fieldtype": "Text Editor", "label": "Notes"},
    ]
    _create_doctype("Die Master", fields,
                    autoname="field:die_code",
                    title_field="die_name",
                    search_fields="die_code,die_name",
                    naming_rule="By fieldname")


def create_frame_master():
    fields = [
        {"fieldname": "frame_code", "fieldtype": "Data", "label": "Frame Code", "reqd": 1, "unique": 1, "in_list_view": 1, "bold": 1},
        {"fieldname": "frame_name", "fieldtype": "Data", "label": "Frame Name", "reqd": 1, "in_list_view": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status",
         "options": "Active\nInactive\nRetired\nUnder Repair", "default": "Active", "in_list_view": 1},
        {"fieldname": "section_details", "fieldtype": "Section Break", "label": "Details"},
        {"fieldname": "frame_type", "fieldtype": "Select", "label": "Type",
         "options": "SCREEN_PRINTING\nPAD_PRINTING\nEMBOSSING\nHOLDING\nJIG_FIXTURE"},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "storage_location", "fieldtype": "Data", "label": "Storage Location"},
        {"fieldname": "current_machine", "fieldtype": "Link", "label": "On Machine", "options": "Workstation"},
        {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"},
    ]
    _create_doctype("Frame Master", fields,
                    autoname="field:frame_code",
                    title_field="frame_name",
                    search_fields="frame_code,frame_name",
                    naming_rule="By fieldname")


def create_kc_delivery_note_item():
    fields = [
        {"fieldname": "item_code", "fieldtype": "Link", "label": "Item", "options": "Item", "reqd": 1, "in_list_view": 1},
        {"fieldname": "qty", "fieldtype": "Float", "label": "Quantity", "reqd": 1, "in_list_view": 1},
        {"fieldname": "uom", "fieldtype": "Link", "label": "UOM", "options": "UOM", "in_list_view": 1},
        {"fieldname": "batch_no", "fieldtype": "Data", "label": "Batch"},
        {"fieldname": "notes", "fieldtype": "Small Text", "label": "Notes"},
    ]
    _create_doctype("KC Delivery Note Item", fields, istable=1)


def create_kc_delivery_note():
    fields = [
        {"fieldname": "section_route", "fieldtype": "Section Break", "label": "Route"},
        {"fieldname": "direction", "fieldtype": "Select", "label": "Direction", "reqd": 1, "in_list_view": 1,
         "options": "KC → Main\nMain → KC"},
        {"fieldname": "from_warehouse", "fieldtype": "Link", "label": "From Warehouse", "options": "Warehouse", "reqd": 1},
        {"fieldname": "to_warehouse", "fieldtype": "Link", "label": "To Warehouse", "options": "Warehouse", "reqd": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number"},
        {"fieldname": "driver_name", "fieldtype": "Data", "label": "Driver"},
        {"fieldname": "driver_phone", "fieldtype": "Data", "label": "Driver Phone"},
        {"fieldname": "section_timing", "fieldtype": "Section Break", "label": "Timing & Scan"},
        {"fieldname": "dispatched_at", "fieldtype": "Datetime", "label": "Dispatched At"},
        {"fieldname": "dispatched_by", "fieldtype": "Link", "label": "Dispatched By", "options": "Employee"},
        {"fieldname": "dispatch_scan", "fieldtype": "Data", "label": "Dispatch QR Scan"},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "received_at", "fieldtype": "Datetime", "label": "Received At"},
        {"fieldname": "received_by", "fieldtype": "Link", "label": "Received By", "options": "Employee"},
        {"fieldname": "receipt_scan", "fieldtype": "Data", "label": "Receipt QR Scan"},
        {"fieldname": "section_items", "fieldtype": "Section Break", "label": "Items"},
        {"fieldname": "items", "fieldtype": "Table", "label": "Items", "options": "KC Delivery Note Item", "reqd": 1},
        {"fieldname": "section_status", "fieldtype": "Section Break", "label": "Status"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status", "in_list_view": 1,
         "options": "Draft\nDispatched\nIn Transit\nReceived\nDiscrepancy\nCancelled", "default": "Draft"},
        {"fieldname": "discrepancy_notes", "fieldtype": "Small Text", "label": "Discrepancy Notes",
         "depends_on": "eval:doc.status == 'Discrepancy'"},
        {"fieldname": "papa_confirmed", "fieldtype": "Check", "label": "Papa Confirmed (WhatsApp)", "default": 0,
         "description": "KC Papa has confirmed this delivery via WhatsApp"},
        {"fieldname": "amended_from", "fieldtype": "Link", "label": "Amended From", "options": "KC Delivery Note",
         "no_copy": 1, "print_hide": 1, "read_only": 1},
    ]
    _create_doctype("KC Delivery Note", fields,
                    autoname="format:KCDN-{YYYY}-{#####}",
                    title_field="direction",
                    search_fields="vehicle_number,driver_name,status",
                    naming_rule="Expression",
                    is_submittable=1)


def create_shift_handover():
    fields = [
        {"fieldname": "section_basic", "fieldtype": "Section Break", "label": "Shift Details"},
        {"fieldname": "handover_date", "fieldtype": "Date", "label": "Date", "reqd": 1, "in_list_view": 1, "default": "Today"},
        {"fieldname": "outgoing_shift", "fieldtype": "Link", "label": "Outgoing Shift", "options": "Shift Type", "reqd": 1},
        {"fieldname": "incoming_shift", "fieldtype": "Link", "label": "Incoming Shift", "options": "Shift Type"},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "outgoing_supervisor", "fieldtype": "Link", "label": "Outgoing Supervisor", "options": "Employee", "reqd": 1, "in_list_view": 1},
        {"fieldname": "incoming_supervisor", "fieldtype": "Link", "label": "Incoming Supervisor", "options": "Employee"},
        {"fieldname": "department", "fieldtype": "Link", "label": "Department", "options": "Department"},
        {"fieldname": "section_production", "fieldtype": "Section Break", "label": "Production"},
        {"fieldname": "machines_running", "fieldtype": "Int", "label": "Machines Running"},
        {"fieldname": "machines_idle", "fieldtype": "Int", "label": "Machines Idle"},
        {"fieldname": "machines_breakdown", "fieldtype": "Int", "label": "Machines Breakdown"},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "wip_count", "fieldtype": "Int", "label": "WIP Count (pieces)"},
        {"fieldname": "shift_output", "fieldtype": "Int", "label": "Shift Output (pieces)"},
        {"fieldname": "rejections", "fieldtype": "Int", "label": "Rejections"},
        {"fieldname": "section_notes", "fieldtype": "Section Break", "label": "Handover Notes"},
        {"fieldname": "pending_issues", "fieldtype": "Text Editor", "label": "Pending Issues"},
        {"fieldname": "notes_for_next_shift", "fieldtype": "Text Editor", "label": "Notes for Next Shift", "reqd": 1},
        {"fieldname": "section_ack", "fieldtype": "Section Break", "label": "Acknowledgement", "collapsible": 1},
        {"fieldname": "acknowledged_by_incoming", "fieldtype": "Check", "label": "Acknowledged by Incoming Supervisor"},
        {"fieldname": "acknowledged_at", "fieldtype": "Datetime", "label": "Acknowledged At", "read_only": 1},
    ]
    _create_doctype("Shift Handover", fields,
                    autoname="format:SH-{YYYY}-{MM}-{#####}",
                    title_field="handover_date",
                    search_fields="outgoing_supervisor,department,handover_date",
                    naming_rule="Expression")


def create_panic_alert():
    fields = [
        {"fieldname": "section_alert", "fieldtype": "Section Break", "label": "Alert"},
        {"fieldname": "alert_type", "fieldtype": "Select", "label": "Type", "reqd": 1, "in_list_view": 1,
         "options": "Machine Breakdown\nSafety Incident\nMaterial Shortage\nQuality Issue\nMedical Emergency\nFire/Safety\nOther"},
        {"fieldname": "severity", "fieldtype": "Select", "label": "Severity", "reqd": 1, "in_list_view": 1,
         "options": "Critical\nHigh\nMedium\nLow", "default": "High"},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "raised_at", "fieldtype": "Datetime", "label": "Raised At", "reqd": 1, "default": "Now", "read_only": 1},
        {"fieldname": "raised_by", "fieldtype": "Link", "label": "Raised By", "options": "Employee", "reqd": 1, "in_list_view": 1},
        {"fieldname": "section_context", "fieldtype": "Section Break", "label": "Context"},
        {"fieldname": "location", "fieldtype": "Data", "label": "Location"},
        {"fieldname": "machine", "fieldtype": "Link", "label": "Machine", "options": "Workstation"},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "department", "fieldtype": "Link", "label": "Department", "options": "Department"},
        {"fieldname": "photo", "fieldtype": "Attach Image", "label": "Photo"},
        {"fieldname": "section_desc", "fieldtype": "Section Break", "label": "Description"},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Description"},
        {"fieldname": "section_assign", "fieldtype": "Section Break", "label": "Assignment"},
        {"fieldname": "assigned_to", "fieldtype": "Link", "label": "Assigned To (Supervisor)", "options": "Employee"},
        {"fieldname": "whatsapp_sent", "fieldtype": "Check", "label": "WhatsApp Sent", "default": 0},
        {"fieldname": "col_3", "fieldtype": "Column Break"},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status", "in_list_view": 1,
         "options": "Open\nAcknowledged\nIn Progress\nResolved\nFalse Alarm", "default": "Open"},
        {"fieldname": "resolved_at", "fieldtype": "Datetime", "label": "Resolved At", "read_only": 1},
        {"fieldname": "section_resolution", "fieldtype": "Section Break", "label": "Resolution", "collapsible": 1},
        {"fieldname": "resolution_notes", "fieldtype": "Text Editor", "label": "Resolution Notes"},
    ]
    _create_doctype("Panic Alert", fields,
                    autoname="format:PA-{YYYY}-{MM}-{DD}-{#####}",
                    title_field="alert_type",
                    search_fields="alert_type,severity,status,raised_by",
                    naming_rule="Expression")


# ────────────────────────────────────────────────────────
# Custom Fields on Standard DocTypes
# ────────────────────────────────────────────────────────


def _add_custom_field(doctype: str, fieldname: str, spec: dict) -> None:
    if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
        print(f"  [=] Custom field {doctype}.{fieldname} exists")
        return
    cf = frappe.new_doc("Custom Field")
    cf.dt = doctype
    cf.fieldname = fieldname
    cf.module = MODULE
    for k, v in spec.items():
        setattr(cf, k, v)
    cf.insert(ignore_permissions=True)
    print(f"  [+] Custom field: {doctype}.{fieldname}")


def add_item_custom_fields():
    fields = [
        ("genauto_gasket_section", {"fieldtype": "Section Break", "label": "Gasket Details",
                                     "insert_after": "item_group", "collapsible": 0}),
        ("brand_genauto", {"fieldtype": "Select", "label": "Brand",
                           "options": "\nGENERAL\nAION\nGENAUTO\nCOMMON",
                           "insert_after": "genauto_gasket_section", "in_list_view": 1, "in_standard_filter": 1}),
        ("product_type", {"fieldtype": "Select", "label": "Product Type",
                          "options": "\nFULL_KIT_A\nDECARB_KIT_B\nSINGLE\nCLUTCH_COVER\nWITH_ORING_R\nHEAD_GASKET\nWIREMESH_EXHAUST\nASB_EXHAUST",
                          "insert_after": "brand_genauto", "in_standard_filter": 1}),
        ("vehicle_category", {"fieldtype": "Select", "label": "Vehicle Category",
                               "options": "\nHONDA\nBAJAJ\nTVS\nYAMAHA\nSUZUKI\nROYAL ENFIELD\nHERO\nMAHINDRA\nMARUTI\nTATA\nASHOK LEYLAND\nOTHER",
                               "insert_after": "product_type", "in_standard_filter": 1}),
        ("col_gasket_1", {"fieldtype": "Column Break", "insert_after": "vehicle_category"}),
        ("die_code_link", {"fieldtype": "Link", "label": "Die", "options": "Die Master",
                           "insert_after": "col_gasket_1"}),
        ("frame_code_link", {"fieldtype": "Link", "label": "Frame", "options": "Frame Master",
                             "insert_after": "die_code_link"}),
        ("rack_location", {"fieldtype": "Data", "label": "Rack Location",
                           "insert_after": "frame_code_link"}),
        ("ddmrp_section", {"fieldtype": "Section Break", "label": "DDMRP / Planning",
                           "insert_after": "rack_location", "collapsible": 1}),
        ("buffer_zone", {"fieldtype": "Select", "label": "Buffer Zone",
                         "options": "\nGREEN\nYELLOW\nRED",
                         "insert_after": "ddmrp_section"}),
        ("abc_class", {"fieldtype": "Select", "label": "ABC Class",
                       "options": "\nA\nB\nC", "insert_after": "buffer_zone"}),
        ("col_ddmrp_1", {"fieldtype": "Column Break", "insert_after": "abc_class"}),
        ("xyz_class", {"fieldtype": "Select", "label": "XYZ Class",
                       "options": "\nX\nY\nZ", "insert_after": "col_ddmrp_1"}),
        ("replenishment_method", {"fieldtype": "Select", "label": "Replenishment",
                                   "options": "\nMAKE\nBUY\nMAKE_KC\nTRADE",
                                   "insert_after": "xyz_class"}),
        ("alignbooks_id", {"fieldtype": "Data", "label": "AlignBooks ID", "read_only": 1, "no_copy": 1,
                           "insert_after": "replenishment_method",
                           "description": "Legacy AlignBooks identifier for migration tracking"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Item", fieldname, spec)


def add_employee_custom_fields():
    fields = [
        ("genauto_floor_section", {"fieldtype": "Section Break", "label": "Factory Floor Settings",
                                     "insert_after": "attendance_device_id", "collapsible": 1}),
        ("nfc_card_uid", {"fieldtype": "Data", "label": "NFC Card UID",
                          "insert_after": "genauto_floor_section",
                          "description": "UID of the employee's NFC access badge"}),
        ("language_preference", {"fieldtype": "Select", "label": "Language Preference",
                                  "options": "\nhi\nen", "default": "hi",
                                  "insert_after": "nfc_card_uid"}),
        ("col_floor_1", {"fieldtype": "Column Break", "insert_after": "language_preference"}),
        ("skill_matrix_iluo", {"fieldtype": "Select", "label": "Skill Matrix (ILUO)",
                                "options": "\nI\nL\nU\nO",
                                "insert_after": "col_floor_1",
                                "description": "I=In training, L=Learning, U=Under supervision, O=Operator (independent)"}),
        ("pin_4digit", {"fieldtype": "Password", "label": "4-digit PIN",
                         "insert_after": "skill_matrix_iluo",
                         "description": "Short PIN for worker PWA login"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Employee", fieldname, spec)


def add_customer_custom_fields():
    fields = [
        ("region_genauto", {"fieldtype": "Select", "label": "Region",
                             "options": "\nNorth\nSouth\nEast\nWest\nCentral\nExports",
                             "insert_after": "customer_group", "in_standard_filter": 1}),
        ("assigned_asm", {"fieldtype": "Link", "label": "Assigned ASM (Area Sales Manager)", "options": "User",
                          "insert_after": "region_genauto"}),
        ("buffer_days_target", {"fieldtype": "Int", "label": "Buffer Days Target",
                                  "insert_after": "assigned_asm",
                                  "description": "Customer expects this many days of safety stock"}),
        ("alignbooks_id_cust", {"fieldtype": "Data", "label": "AlignBooks ID", "read_only": 1, "no_copy": 1,
                                "insert_after": "buffer_days_target"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Customer", fieldname, spec)


def add_supplier_custom_fields():
    fields = [
        ("alignbooks_id_supp", {"fieldtype": "Data", "label": "AlignBooks ID", "read_only": 1, "no_copy": 1,
                                  "insert_after": "supplier_group"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Supplier", fieldname, spec)


def add_workstation_custom_fields():
    fields = [
        ("machine_type", {"fieldtype": "Select", "label": "Machine Type",
                           "options": "\nPOWER_PRESS\nHAND_PRESS\nSCREEN_AUTO\nSCREEN_SEMI\nSCREEN_MANUAL\nPAD_PRINTER\nGUILLOTINE\nKNITTING\nROLLER_PRESS\nPAINT_BOOTH\nOVEN\nLASER\nRIVETING\nBAND_SEALER\nINKJET\nSHRINK_WRAP\nSLITTER\nPASTING\nEYELET_PUNCHING",
                           "insert_after": "workstation_name", "in_list_view": 1, "in_standard_filter": 1}),
        ("tonnage", {"fieldtype": "Float", "label": "Tonnage",
                      "insert_after": "machine_type"}),
        ("current_die", {"fieldtype": "Link", "label": "Current Die", "options": "Die Master",
                          "insert_after": "tonnage"}),
        ("current_frame", {"fieldtype": "Link", "label": "Current Frame", "options": "Frame Master",
                            "insert_after": "current_die"}),
        ("stroke_counter", {"fieldtype": "Int", "label": "Stroke Counter", "default": 0,
                             "insert_after": "current_frame"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Workstation", fieldname, spec)


def add_work_order_custom_fields():
    fields = [
        ("die_used", {"fieldtype": "Link", "label": "Die Used", "options": "Die Master",
                       "insert_after": "bom_no"}),
        ("frame_used", {"fieldtype": "Link", "label": "Frame Used", "options": "Frame Master",
                         "insert_after": "die_used"}),
        ("kc_dispatch_required", {"fieldtype": "Check", "label": "KC Dispatch Required",
                                    "insert_after": "frame_used",
                                    "description": "Work order output must be dispatched to KC Industries"}),
    ]
    for fieldname, spec in fields:
        _add_custom_field("Work Order", fieldname, spec)


# ────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────


def setup_all():
    print("═" * 60)
    print("  Genauto Gasket Bootstrap")
    print("═" * 60)
    print("\n▶ Creating DocTypes...")
    create_vehicle_application()
    create_die_master()
    create_frame_master()
    create_kc_delivery_note_item()
    create_kc_delivery_note()
    create_shift_handover()
    create_panic_alert()

    print("\n▶ Adding Custom Fields to Item...")
    add_item_custom_fields()
    print("\n▶ Adding Custom Fields to Employee...")
    add_employee_custom_fields()
    print("\n▶ Adding Custom Fields to Customer...")
    add_customer_custom_fields()
    print("\n▶ Adding Custom Fields to Supplier...")
    add_supplier_custom_fields()
    print("\n▶ Adding Custom Fields to Workstation...")
    add_workstation_custom_fields()
    print("\n▶ Adding Custom Fields to Work Order...")
    add_work_order_custom_fields()

    frappe.db.commit()
    print("\n" + "═" * 60)
    print("  ✓ Bootstrap complete")
    print("═" * 60)
