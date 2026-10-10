"""Input validation and regex helpers for Employee Payroll System."""

import re
from datetime import datetime
from exceptions import InvalidPayrollDataError

DATE_PATTERN = r"^(\d{4})-(\d{2})-(\d{2})$"
MONTH_PATTERN = r"^(\d{4})-(0[1-9]|1[0-2])$"
NAME_PATTERN = r"^[A-Za-z]+( [A-Za-z]+)*$"
EMP_ID_PATTERN = r"^EMP\d{3,6}$"
DEPT_PATTERN = r"^[A-Za-z &/]+$"


def validate_date(text):
    text = text.strip()
    match = re.match(DATE_PATTERN, text)
    if match is None:
        raise InvalidPayrollDataError(f"Date '{text}' must look like YYYY-MM-DD")
    year, month, day = match.groups()
    try:
        datetime(int(year), int(month), int(day))
    except ValueError:
        raise InvalidPayrollDataError(f"Date '{text}' does not exist in the calendar")
    return text


def validate_pay_month(text):
    text = text.strip()
    if re.match(MONTH_PATTERN, text) is None:
        raise InvalidPayrollDataError(f"Pay month '{text}' must look like YYYY-MM (e.g. 2024-01)")
    return text


def split_date(text):
    match = re.match(DATE_PATTERN, text)
    if match:
        return match.groups()
    return None


def clean_name(text, label, pattern=NAME_PATTERN):
    cleaned = re.sub(r"\s+", " ", text.strip())
    if re.match(pattern, cleaned) is None:
        raise InvalidPayrollDataError(f"{label} '{cleaned}' must contain letters and spaces only")
    return cleaned.title()


def validate_name(name):
    return clean_name(name, "Employee name")


def validate_department(dept):
    cleaned = dept.strip()
    if re.match(DEPT_PATTERN, cleaned) is None:
        raise InvalidPayrollDataError(f"Department '{cleaned}' has invalid characters")
    return cleaned.title()


def validate_emp_id(emp_id):
    emp_id = emp_id.strip().upper()
    if re.match(EMP_ID_PATTERN, emp_id) is None:
        raise InvalidPayrollDataError(f"Employee ID '{emp_id}' must be like EMP001 ... EMP999999")
    return emp_id


def validate_salary(text, field_name):
    try:
        value = float(text.strip().replace(",", ""))
    except ValueError:
        raise InvalidPayrollDataError(f"{field_name} must be a number, got '{text}'")
    if value < 0:
        raise InvalidPayrollDataError(f"{field_name} cannot be negative ({value})")
    return round(value, 2)


def validate_gender(text):
    text = text.strip().title()
    if text not in ("Male", "Female", "Other"):
        raise InvalidPayrollDataError(f"Gender must be Male/Female/Other, got '{text}'")
    return text


def validate_record(record):
    validate_emp_id(record["EmpID"])
    validate_name(record["Name"])
    validate_date(record["JoinDate"])
    validate_pay_month(record["PayMonth"])
    if record["BasicSalary"] <= 0:
        raise InvalidPayrollDataError("Basic Salary must be positive")
    if record["TotalDeductions"] > record["GrossSalary"]:
        raise InvalidPayrollDataError("Total deductions cannot exceed gross salary")
    if record["NetSalary"] < 0:
        raise InvalidPayrollDataError("Net salary cannot be negative")
    return True


def regex_search_employee(records, pattern, field="Name"):
    results = []
    for record in records:
        try:
            match = re.search(pattern, record.get(field, ""), re.IGNORECASE)
        except re.error:
            raise InvalidPayrollDataError(f"'{pattern}' is not a valid regular expression")
        if match:
            results.append((record, match))
    return results


def highlight(pattern, text):
    return re.sub(pattern, lambda m: "[" + m.group() + "]", text, flags=re.IGNORECASE)
