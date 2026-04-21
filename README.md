# Genauto Gasket — ERPNext Custom App

Gasket-manufacturing extensions for **Genauto Gasket Technologies LLP** on ERPNext v16.

## Contents

### Custom DocTypes (`genauto_gasket/doctype/`)
| DocType | Purpose |
|---|---|
| **Vehicle Application** | Gasket ↔ vehicle cross-reference (OEM part numbers, competitor refs) |
| **Die Master** | Tooling catalog with stroke counter, machine assignment |
| **Frame Master** | Secondary tooling (screen/pad printing frames) |
| **KC Delivery Note** (submittable) | Inter-factory transit Main ↔ KC Industries with QR scan in/out |
| **KC Delivery Note Item** (child) | Line items on KC Delivery Note |
| **Shift Handover** | End-of-shift notes, WIP count, machines state |
| **Panic Alert** | Factory-floor escalation with severity, WhatsApp integration |

### Custom Fields
- **Item**: brand, product_type, vehicle_category, die_code, frame_code, rack_location, DDMRP buffer_zone, abc_class, xyz_class, replenishment, alignbooks_id (15 fields)
- **Employee**: attendance_device_id (native), nfc_card_uid, language_preference, skill_matrix_iluo, pin_4digit (6)
- **Customer**: region, assigned_asm, buffer_days_target, alignbooks_id (4)
- **Supplier**: alignbooks_id (1)
- **Workstation**: machine_type (gasket-specific), tonnage, current_die, current_frame, stroke_counter (5)
- **Work Order**: die_used, frame_used, kc_dispatch_required (3)

**Total: 34 custom fields across 6 standard DocTypes.**

## Ancillary Scripts

### `bootstrap.py`
One-time setup: creates all DocTypes + custom fields. Run:
```bash
bench --site erp.genautoindia.com execute genauto_gasket.bootstrap.setup_all
```

### `employees.py`
Bulk imports 86 employees from eSSL biometric roster, maps PIN → `attendance_device_id`, creates service user for bridge. Run:
```bash
bench --site erp.genautoindia.com execute genauto_gasket.employees.setup_all
```

### `zkteco-bridge.py` + `zkteco-bridge.service`
Sidecar systemd service polling `/opt/eSSL-attlog/data/attendance.jsonl` every 30 s and POSTing to ERPNext `Employee Checkin` API. Deploy to `/home/master/zkteco-bridge/sync.py` + `/etc/systemd/system/zkteco-bridge.service` with creds at `/etc/zkteco-bridge.env`.

## Install

```bash
bench get-app https://github.com/genauto-git/genauto_gasket --branch main
bench --site <site> install-app genauto_gasket
bench --site <site> execute genauto_gasket.bootstrap.setup_all
bench --site <site> execute genauto_gasket.employees.setup_all
bench --site <site> migrate
```

## Requires
- Frappe v16
- ERPNext v16
- HRMS v16
- India Compliance v16
- Print Designer (main)

## License
MIT
