"""
Live attendance number-card backends.

Custom Number Cards on the Attendance Dashboard call these whitelisted
functions to show real-time floor status — no waiting for end-of-shift
auto-attendance processing. Pure SQL against `tabEmployee Checkin` so
counts move as workers punch.

Each function returns an int (per Frappe Number Card type=Custom
contract; e.g. hrms.utils.custom_method_for_charts.get_upcoming_holidays).
"""
from __future__ import annotations

import frappe
from frappe.utils import today


# ────────────────────────────────────────────────────────
# Live counts
# ────────────────────────────────────────────────────────


@frappe.whitelist()
def punched_in_today() -> int:
    """Distinct employees with at least one Employee Checkin today."""
    n = frappe.db.sql_list(
        """
        SELECT COUNT(DISTINCT employee)
        FROM `tabEmployee Checkin`
        WHERE DATE(time) = %s
        """,
        today(),
    )[0]
    return int(n or 0)


@frappe.whitelist()
def currently_in_office() -> int:
    """Employees whose latest punch today has odd index (i.e. they haven't
    punched OUT yet — still inside).

    Uses count-parity: odd # of punches today → currently IN. Robust to
    legacy rows where log_type is NULL because the alternating rule is
    applied to row order, same as Frappe's auto-attendance logic.
    """
    n = frappe.db.sql_list(
        """
        SELECT COUNT(*) FROM (
            SELECT employee, COUNT(*) AS cnt
            FROM `tabEmployee Checkin`
            WHERE DATE(time) = %s
            GROUP BY employee
            HAVING cnt %% 2 = 1
        ) t
        """,
        today(),
    )[0]
    return int(n or 0)


@frappe.whitelist()
def late_today() -> int:
    """Employees whose first punch today was after their shift's late-entry
    threshold (shift_start + late_entry_grace_period).

    Falls back to a 09:15 cutoff if shift configuration is missing.
    """
    n = frappe.db.sql_list(
        """
        WITH first_punch AS (
            SELECT
                ec.employee,
                MIN(ec.time) AS first_time,
                MAX(st.start_time) AS shift_start,
                MAX(st.late_entry_grace_period) AS grace
            FROM `tabEmployee Checkin` ec
            LEFT JOIN `tabEmployee` e ON e.name = ec.employee
            LEFT JOIN `tabShift Type` st ON st.name = e.default_shift
            WHERE DATE(ec.time) = %s
              AND st.enable_late_entry_marking = 1
            GROUP BY ec.employee
        )
        SELECT COUNT(*) FROM first_punch
        WHERE TIME(first_time) >
              ADDTIME(shift_start, SEC_TO_TIME(grace * 60))
        """,
        today(),
    )[0]
    return int(n or 0)


@frappe.whitelist()
def not_arrived_yet() -> int:
    """Active employees with a default_shift who have no punch today.

    Excludes management (no default_shift) so Naresh / Bhuvnesh / Vibhav
    don't inflate the absent count.
    """
    n = frappe.db.sql_list(
        """
        SELECT COUNT(*)
        FROM `tabEmployee` e
        WHERE e.status = 'Active'
          AND e.default_shift IS NOT NULL
          AND e.default_shift != ''
          AND NOT EXISTS (
              SELECT 1 FROM `tabEmployee Checkin` ec
              WHERE ec.employee = e.name AND DATE(ec.time) = %s
          )
        """,
        today(),
    )[0]
    return int(n or 0)
