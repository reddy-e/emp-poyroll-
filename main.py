"""Employee Payroll System - main menu and user interaction.
Run with:  python main.py
"""

from datetime import datetime

import analyzer
import file_utils
import validators
from exceptions import InvalidPayrollDataError

MENU = """
========================================
      EMPLOYEE PAYROLL SYSTEM
========================================
 1. View Payroll Records
 2. Add Employee Record
 3. Search Employee
 4. Validate Data
 5. Analyze Department
 6. Analyze by Designation
 7. Generate Summary Report
 8. Top Earners Report
 9. Backup Data
10. Restore Backup
11. Copy Data File
12. Merge Data Files
 0. Exit
"""


def load_records():
    try:
        return file_utils.read_records()
    except FileNotFoundError:
        print("Data file not found! Please place payroll_data.csv in the data/ folder.")
    except InvalidPayrollDataError as error:
        print(f"Invalid data: {error}")
    return []


def print_table(records):
    print(f"\n{'EmpID':<10}{'Name':<22}{'Department':<15}{'Designation':<18}"
          f"{'PayMonth':<10}{'Gross':>12}{'Net':>12}{'Deductions':>12}")
    print("-" * 115)
    for r in records:
        print(f"{r.get('EmpID', ''):<10}{r['Name']:<22}{r['Department']:<15}"
              f"{r['Designation']:<18}{r.get('PayMonth', ''):<10}"
              f"{r.get('GrossSalary', 0):>12,.2f}"
              f"{r.get('NetSalary', 0):>12,.2f}"
              f"{r.get('TotalDeductions', 0):>12,.2f}")
    print(f"\nRecords shown:\t{len(records)}")


def show_stats(title, stats):
    print(f"\n--- {title} ---")
    for label, value in stats.items():
        if "Rate" in label or "%" in label:
            print(f"{label:<30}: {value}%")
        elif isinstance(value, (int, float)):
            print(f"{label:<30}: {value:,.2f}")
        else:
            print(f"{label:<30}: {value}")


# 1. VIEW
def view_data():
    records = load_records()
    if len(records) == 0:
        print("No records to show.")
        return
    print("Payroll Data Summary:")
    print_table(records)
    print(f"Lines in file (including header): {file_utils.count_lines()}")


# 2. ADD
def add_record():
    print("\n--- Add Employee Payroll Record ---")
    try:
        emp_id = validators.validate_emp_id(input("Employee ID (e.g. EMP001): "))
        name = validators.validate_name(input("Full Name: "))
        dept = validators.validate_department(input("Department: "))
        desig = input("Designation: ").strip()
        if not desig:
            raise InvalidPayrollDataError("Designation cannot be empty")
        gender = validators.validate_gender(input("Gender (Male/Female/Other): "))
        join_date = validators.validate_date(input("Join Date (YYYY-MM-DD): "))
        pay_month = validators.validate_pay_month(input("Pay Month (YYYY-MM): "))
        basic = validators.validate_salary(input("Basic Salary: "), "Basic Salary")
        hra = validators.validate_salary(input("HRA: "), "HRA")
        allowances = validators.validate_salary(input("Allowances: "), "Allowances")
        pf = validators.validate_salary(input("PF Deduction: "), "PF Deduction")
        tax = validators.validate_salary(input("Tax Deduction: "), "Tax Deduction")
        other = validators.validate_salary(input("Other Deductions: "), "Other Deductions")

        record = analyzer.make_record(
            emp_id=emp_id, name=name, department=dept, designation=desig,
            gender=gender, join_date=join_date, pay_month=pay_month,
            basic_salary=basic, hra=hra, allowances=allowances,
            pf_deduction=pf, tax_deduction=tax, other_deductions=other,
        )
        validators.validate_record(record)
    except InvalidPayrollDataError as error:
        print(f"Invalid data: {error}")
    else:
        file_utils.append_record(record)
        print(f"Record saved!  Gross = {record['GrossSalary']:,.2f}  |  Net = {record['NetSalary']:,.2f}")
    finally:
        print("--- Add record finished ---")


# 3. SEARCH
def search_data():
    records = load_records()
    print("\n1. Search by Name (full or partial)\n2. Search by Department\n3. Regex search on Name\n4. Search by EmpID")
    choice = input("Choose search type: ").strip()
    found = []

    if choice == "1":
        term = input("Employee name: ").strip().lower()
        if term == "":
            print("Nothing entered.")
            return
        for record in records:
            name_lower = record["Name"].lower()
            if term == name_lower:
                found.append(record)
                print(f"  {record['Name']:<22} exact match")
            elif name_lower.startswith(term):
                found.append(record)
                print(f"  {record['Name']:<22} starts with '{term}'")
            elif term in name_lower:
                found.append(record)
                print(f"  {record['Name']:<22} contains '{term}'")
    elif choice == "2":
        term = input("Department: ").strip().lower()
        for record in records:
            if term != "" and term in record.get("Department", "").lower():
                found.append(record)
    elif choice == "3":
        pattern = input("Regex pattern (e.g. ^A, son$, kumar): ").strip()
        try:
            results = validators.regex_search_employee(records, pattern, field="Name")
        except InvalidPayrollDataError as error:
            print(f"Invalid data: {error}")
            return
        for record, match in results:
            found.append(record)
            print(f"{validators.highlight(pattern, record['Name']):<22} "
                  f"match='{match.group()}'  span={match.span()}")
    elif choice == "4":
        term = input("Employee ID (e.g. EMP001): ").strip().upper()
        for record in records:
            if record["EmpID"].upper() == term:
                found.append(record)
    else:
        print("Invalid search type.")
        return

    if len(found) == 0:
        print("No matching records.")
    else:
        print_table(found)


# 4. VALIDATE
def validate_data():
    records = load_records()
    print("\n--- Validate Data ---")
    valid = 0
    invalid = 0
    for record in records:
        try:
            validators.validate_record(record)
        except InvalidPayrollDataError as error:
            print(f"Invalid: {record.get('EmpID')} ({record.get('Name')}) -> {error}")
            invalid += 1
            continue
        valid += 1
    print(f"Valid records: {valid} | Invalid records: {invalid}")

    text = input("\nType an Employee ID to test (e.g. EMP001): ").strip()
    if text:
        try:
            result = validators.validate_emp_id(text)
            print(f"Valid Employee ID: {result}")
        except InvalidPayrollDataError as error:
            print(f"Invalid: {error}")

    month = input("Type a pay month to test (YYYY-MM): ").strip()
    if month:
        try:
            result = validators.validate_pay_month(month)
            print(f"Valid Pay Month: {result}")
        except InvalidPayrollDataError as error:
            print(f"Invalid: {error}")


# 5. DEPARTMENT ANALYSIS
def analyze_department():
    records = load_records()
    try:
        dept = validators.validate_department(input("\nEnter department name: "))
    except InvalidPayrollDataError as error:
        print(f"Invalid data: {error}")
        return
    subset = analyzer.filter_by_department(records, dept)
    if len(subset) == 0:
        print(f"No records found for department '{dept}'.")
        return
    stats = analyzer.summarize(subset)
    show_stats(f"Department: {dept}", stats)
    print("\nTop 5 earners in this department:")
    print_table(analyzer.top_earners(subset, "NetSalary", 5))


# 6. DESIGNATION ANALYSIS
def analyze_designation():
    records = load_records()
    desig = input("\nEnter designation: ").strip()
    if not desig:
        print("Designation cannot be empty.")
        return
    subset = analyzer.filter_by_designation(records, desig)
    if len(subset) == 0:
        print(f"No records found for designation '{desig}'.")
        return
    stats = analyzer.summarize(subset)
    show_stats(f"Designation: {desig}", stats)
    print_table(subset[:10])


# 7. SUMMARY REPORT
def summary_report():
    records = load_records()
    stats = analyzer.summarize(records)
    if stats is None:
        print("No data to summarize.")
        return
    print(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    show_stats("OVERALL PAYROLL SUMMARY (all employees - latest snapshots)", stats)

    print(f"\n{'Department':<18}{'Employees':>10}{'Total Gross':>14}{'Total Net':>14}"
          f"{'Avg Net':>12}{'Deduction%':>12}")
    print("-" * 84)
    dept_summaries = analyzer.department_summary(records)
    for dept, s in dept_summaries:
        print(f"{dept:<18}{s['Employees']:>10}"
              f"{s['Total Gross Salary']:>14,.2f}"
              f"{s['Total Net Salary']:>14,.2f}"
              f"{s['Average Net Salary']:>12,.2f}"
              f"{s['Deduction Rate (%)']:>12}")

    print("\nTop 5 earners overall (by Net Salary):")
    print_table(analyzer.top_earners(records, "NetSalary", 5))
    print("\nTop 5 by Gross Salary:")
    print_table(analyzer.top_earners(records, "GrossSalary", 5))


# 8. TOP EARNERS
def top_earners_report():
    records = load_records()
    try:
        n = int(input("\nHow many top earners to show? (default 10): ").strip() or "10")
    except ValueError:
        n = 10
    print(f"\nTop {n} Earners by Net Salary:")
    print_table(analyzer.top_earners(records, "NetSalary", n))


# 9-12. FILE OPERATIONS
def backup():
    records = load_records()
    file_utils.backup_data(records)
    print(f"Backup created: {len(records)} records saved to data/backup.dat")


def restore():
    try:
        records = file_utils.restore_backup()
    except FileNotFoundError:
        print("No backup found. Use option 9 first.")
    else:
        file_utils.save_all(records)
        print(f"Restored {len(records)} records into payroll_data.csv")


def copy_data():
    try:
        size = file_utils.copy_file()
    except FileNotFoundError:
        print("Source file not found!")
    else:
        print(f"Copied payroll_data.csv -> copy.csv ({size} bytes)")


def merge_data():
    first = input("\nFirst file [payroll_data.csv]: ").strip() or "payroll_data.csv"
    second = input("Second file [extra_payroll.csv]: ").strip() or "extra_payroll.csv"
    try:
        count = file_utils.merge_files(
            file_utils.DATA_DIR / first,
            file_utils.DATA_DIR / second
        )
    except FileNotFoundError as error:
        print(error)
    else:
        print(f"Merged {count} unique records into data/merged.csv (one header)")


def main():
    file_utils.ensure_sample_data()
    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print(".....EXITED.....")
            break
        elif choice == "1":
            view_data()
        elif choice == "2":
            add_record()
        elif choice == "3":
            search_data()
        elif choice == "4":
            validate_data()
        elif choice == "5":
            analyze_department()
        elif choice == "6":
            analyze_designation()
        elif choice == "7":
            summary_report()
        elif choice == "8":
            top_earners_report()
        elif choice == "9":
            backup()
        elif choice == "10":
            restore()
        elif choice == "11":
            copy_data()
        elif choice == "12":
            merge_data()
        else:
            print("Invalid choice! Please enter a number from 0 to 12.")
            continue
        try:
            input("\nPress Enter to continue...")
        except EOFError:
            break


if __name__ == "__main__":
    main()
