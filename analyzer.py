"""Payroll calculations, statistics, and analytics for Employee Payroll System."""

import statistics


def calculate_net_salary(basic, hra, allowances, pf_deduction, tax_deduction, other_deductions):
    """Calculate net salary after all deductions."""
    gross = basic + hra + allowances
    total_deductions = pf_deduction + tax_deduction + other_deductions
    net = gross - total_deductions
    return round(net, 2)


def calculate_tax_rate(basic_salary):
    """Simple progressive tax rate calculation."""
    if basic_salary <= 25000:
        return 0.0
    elif basic_salary <= 50000:
        return 5.0
    elif basic_salary <= 100000:
        return 10.0
    elif basic_salary <= 200000:
        return 20.0
    else:
        return 30.0


def make_record(emp_id, name, department, designation, join_date, basic_salary,
                hra, allowances, pf_deduction, tax_deduction, other_deductions,
                pay_month, gender="Unknown"):
    """Create a payroll record dictionary."""
    gross_salary = basic_salary + hra + allowances
    net_salary = calculate_net_salary(basic_salary, hra, allowances,
                                      pf_deduction, tax_deduction, other_deductions)
    total_deductions = pf_deduction + tax_deduction + other_deductions
    return {
        "EmpID": emp_id,
        "Name": name,
        "Department": department,
        "Designation": designation,
        "Gender": gender,
        "JoinDate": join_date,
        "PayMonth": pay_month,
        "BasicSalary": basic_salary,
        "HRA": hra,
        "Allowances": allowances,
        "GrossSalary": gross_salary,
        "PF_Deduction": pf_deduction,
        "Tax_Deduction": tax_deduction,
        "Other_Deductions": other_deductions,
        "TotalDeductions": total_deductions,
        "NetSalary": net_salary,
    }


def total_field(records, field):
    """Sum a numeric field across all records."""
    total = 0.0
    for record in records:
        total += record.get(field, 0)
    return round(total, 2)


def recursive_total(records, field, index=0):
    """Recursively sum a numeric field."""
    if index == len(records):
        return 0.0
    return records[index].get(field, 0) + recursive_total(records, field, index + 1)


def calculate_rate(value, total, precision=2):
    """Return value/total * 100 safely."""
    try:
        return round(value / total * 100, precision)
    except ZeroDivisionError:
        return 0.0


def get_latest_records(records):
    """For each employee, keep only the latest pay-month record."""
    latest = {}
    for r in records:
        emp_id = r["EmpID"]
        if emp_id not in latest or r["PayMonth"] > latest[emp_id]["PayMonth"]:
            latest[emp_id] = r
    return list(latest.values())


def filter_by_department(records, department):
    """Return records matching the given department."""
    return [r for r in records if r["Department"].lower() == department.lower()]


def filter_by_designation(records, designation):
    """Return records matching the given designation."""
    return [r for r in records if r["Designation"].lower() == designation.lower()]


def filter_by_gender(records, gender):
    """Return records matching the given gender."""
    return [r for r in records if r.get("Gender", "").lower() == gender.lower()]


def summarize(records):
    """Produce aggregate statistics for a set of payroll records."""
    if len(records) == 0:
        return None
    latest = get_latest_records(records)
    net_salaries = [r["NetSalary"] for r in latest]
    gross_salaries = [r["GrossSalary"] for r in latest]
    total_net = total_field(latest, "NetSalary")
    total_gross = total_field(latest, "GrossSalary")
    total_deductions = total_field(latest, "TotalDeductions")
    return {
        "Employees": len(latest),
        "Total Gross Salary": round(total_gross, 2),
        "Total Net Salary": round(total_net, 2),
        "Total Deductions": round(total_deductions, 2),
        "Average Net Salary": round(statistics.mean(net_salaries), 2) if net_salaries else 0,
        "Median Net Salary": round(statistics.median(net_salaries), 2) if net_salaries else 0,
        "Highest Net Salary": max(net_salaries) if net_salaries else 0,
        "Lowest Net Salary": min(net_salaries) if net_salaries else 0,
        "Avg Gross Salary": round(statistics.mean(gross_salaries), 2) if gross_salaries else 0,
        "Deduction Rate (%)": calculate_rate(total_deductions, total_gross),
    }


def top_earners(records, field="NetSalary", count=5):
    """Return top N earners by a salary field (latest snapshot per employee)."""
    latest = get_latest_records(records)
    ordered = sorted(latest, key=lambda x: x.get(field, 0), reverse=True)
    return ordered[:count]


def department_summary(records):
    """Return a list of (department, stats) tuples."""
    depts = sorted({r["Department"] for r in records})
    result = []
    for dept in depts:
        subset = filter_by_department(records, dept)
        stats = summarize(subset)
        if stats:
            result.append((dept, stats))
    return result
