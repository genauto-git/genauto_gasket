"""
Genauto wage computation utilities.

Hourly-wage model:
  daily_rate  = monthly_salary / 30
  hourly_rate = daily_rate / 8.5
  regular     = min(working_hours, 8.5)
  ot          = min(max(working_hours - 8.5, 0), 4)
  daily_wage  = regular * hourly_rate
  ot_wage     = ot * hourly_rate * 2     # Factories Act 1948 (2× OT)
  total_pay   = daily_wage + ot_wage

Sundays / Holidays: handled at Salary Slip generation, not Attendance level.
"""
from __future__ import annotations

import frappe
from frappe.utils import flt, today


SHIFT_HOURS = 8.5
OT_MULTIPLIER = 2.0
OT_CAP_HOURS = 4.0           # weekday OT cap (after 8.5h shift)
SUNDAY_OT_CAP_HOURS = 12.5   # Sunday day-window cap (full possible day)


def days_in_month(date) -> int:
    """Calendar days in the month containing `date` (28-31)."""
    import calendar
    from frappe.utils import getdate
    d = getdate(date)
    return calendar.monthrange(d.year, d.month)[1]


def is_sunday(date) -> bool:
    """True if `date` falls on a Sunday (weekday() == 6)."""
    from frappe.utils import getdate
    return getdate(date).weekday() == 6


def compute_wage_fields(working_hours: float, monthly_salary: float,
                         attendance_date=None) -> dict:
    """Pure function — given hours + salary + date, return wage breakdown.

    Weekday: regular up to 8.5h + OT up to 4h (2× rate).
    Sunday: ALL worked hours are OT (2× rate, no regular bucket) — Sunday is
            paid weekly off, so any work is overtime per Factories Act spirit.
    Daily rate uses calendar days in the attendance date's month (Apr 30 →
    ₹500/day, May 31 → ₹483.87/day, Feb 28 → ₹535.71/day).
    """
    if not monthly_salary or monthly_salary <= 0 or not working_hours or working_hours <= 0:
        return {"regular_hours": 0, "ot_hours": 0,
                "daily_wage": 0, "ot_wage": 0, "total_pay": 0}
    if attendance_date is None:
        from frappe.utils import today as _today
        attendance_date = _today()
    n_days = days_in_month(attendance_date)
    daily_rate = monthly_salary / n_days
    hourly_rate = daily_rate / SHIFT_HOURS

    if is_sunday(attendance_date):
        # Sunday work — entire worked time is OT
        regular = 0.0
        ot = min(flt(working_hours), SUNDAY_OT_CAP_HOURS)
    else:
        regular = min(flt(working_hours), SHIFT_HOURS)
        ot = min(max(flt(working_hours) - SHIFT_HOURS, 0), OT_CAP_HOURS)

    daily_wage = regular * hourly_rate
    ot_wage = ot * hourly_rate * OT_MULTIPLIER
    return {
        "regular_hours": round(regular, 2),
        "ot_hours": round(ot, 2),
        "daily_wage": round(daily_wage, 2),
        "ot_wage": round(ot_wage, 2),
        "total_pay": round(daily_wage + ot_wage, 2),
    }


def attendance_set_wages(doc, method=None):
    """Doc-event hook on Attendance before_save / before_submit / on_update.

    Called whether record is created via auto-attendance or manual.
    """
    if not getattr(doc, "employee", None):
        return
    salary = frappe.db.get_value("Employee", doc.employee, "monthly_salary") or 0
    fields = compute_wage_fields(
        doc.working_hours or 0, salary,
        attendance_date=getattr(doc, "attendance_date", None),
    )
    for k, v in fields.items():
        if getattr(doc, k, None) != v:
            setattr(doc, k, v)


# ────────────────────────────────────────────────────────
# Live dashboard methods (Number Card type=Custom)
# ────────────────────────────────────────────────────────


@frappe.whitelist()
def todays_wage_bill_live() -> int:
    """Running today's wage bill — based on live Employee Checkin punches.

    For each employee with checkins today: hours = last_in_to_last_out,
    apply their hourly_rate, sum. Real-time as workers punch.
    """
    rows = frappe.db.sql(
        """
        SELECT ec.employee,
               TIMESTAMPDIFF(SECOND, MIN(ec.time), MAX(ec.time)) / 3600.0 AS hours,
               COALESCE(e.monthly_salary, 0) AS salary
        FROM `tabEmployee Checkin` ec
        JOIN `tabEmployee` e ON e.name = ec.employee
        WHERE DATE(ec.time) = %s
        GROUP BY ec.employee
        HAVING hours > 0
        """,
        today(),
        as_dict=True,
    )
    total = 0.0
    for r in rows:
        wages = compute_wage_fields(r.hours, r.salary, attendance_date=today())
        total += wages["total_pay"]
    return int(round(total))


@frappe.whitelist()
def in_ot_now() -> int:
    """Workers who have been clocked in for > 8.5 hours today already.

    Useful real-time indicator — supervisor can see who's about to enter
    OT zone or already in it.
    """
    n = frappe.db.sql_list(
        """
        SELECT COUNT(*) FROM (
            SELECT employee,
                   TIMESTAMPDIFF(SECOND, MIN(time), MAX(time)) / 3600.0 AS hours
            FROM `tabEmployee Checkin`
            WHERE DATE(time) = %s
            GROUP BY employee
            HAVING hours > 8.5
        ) t
        """,
        today(),
    )[0]
    return int(n or 0)


@frappe.whitelist()
def avg_hours_today() -> float:
    """Average working hours per employee who punched today.

    Quality of attendance metric — if avg = 7.5, factory running healthy.
    If 4-5 = many half-day pattern visible.
    """
    n = frappe.db.sql_list(
        """
        SELECT ROUND(AVG(hours), 1) FROM (
            SELECT TIMESTAMPDIFF(SECOND, MIN(time), MAX(time)) / 3600.0 AS hours
            FROM `tabEmployee Checkin`
            WHERE DATE(time) = %s
            GROUP BY employee
            HAVING hours > 0
        ) t
        """,
        today(),
    )[0]
    return flt(n or 0)


def _month_bounds():
    from frappe.utils import get_first_day, get_last_day, getdate
    today_d = getdate()
    return get_first_day(today_d), get_last_day(today_d)


@frappe.whitelist()
def total_wages_this_month() -> int:
    """Aggregate wages across Attendance records for current month.

    Includes both regular wages and OT wages.
    """
    start, end = _month_bounds()
    n = frappe.db.sql_list(
        """
        SELECT COALESCE(SUM(total_pay), 0)
        FROM `tabAttendance`
        WHERE attendance_date BETWEEN %s AND %s
        """,
        (start, end),
    )[0]
    return int(round(n or 0))


@frappe.whitelist()
def total_ot_hours_this_month() -> float:
    """Aggregate OT hours across all employees this month."""
    start, end = _month_bounds()
    n = frappe.db.sql_list(
        """
        SELECT COALESCE(SUM(ot_hours), 0)
        FROM `tabAttendance`
        WHERE attendance_date BETWEEN %s AND %s
        """,
        (start, end),
    )[0]
    return flt(n or 0)
