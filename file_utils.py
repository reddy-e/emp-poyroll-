"""All file handling: text (CSV), binary (pickle), copy and merge for Payroll System."""

import csv
import os
import pickle
from pathlib import Path

import analyzer
from exceptions import InvalidPayrollDataError

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_FILE = DATA_DIR / "payroll_data.csv"
EXTRA_FILE = DATA_DIR / "extra_payroll.csv"
COPY_FILE = DATA_DIR / "copy.csv"
MERGED_FILE = DATA_DIR / "merged.csv"
BACKUP_FILE = DATA_DIR / "backup.dat"

FIELDS = [
    "EmpID", "Name", "Department", "Designation", "Gender",
    "JoinDate", "PayMonth",
    "BasicSalary", "HRA", "Allowances",
    "PF_Deduction", "Tax_Deduction", "Other_Deductions"
]
HEADER = ",".join(FIELDS)

REQUIRED_COLUMNS = ["EmpID", "Name", "Department", "Designation", "PayMonth", "BasicSalary"]


def to_float(text):
    text = (text or "").replace(",", "").strip()
    if text == "" or text.upper() == "N/A":
        return 0.0
    return round(float(text), 2)


def record_to_line(record):
    values = [
        str(record.get("EmpID", "")),
        str(record.get("Name", "")),
        str(record.get("Department", "")),
        str(record.get("Designation", "")),
        str(record.get("Gender", "Unknown")),
        str(record.get("JoinDate", "")),
        str(record.get("PayMonth", "")),
        str(record.get("BasicSalary", 0)),
        str(record.get("HRA", 0)),
        str(record.get("Allowances", 0)),
        str(record.get("PF_Deduction", 0)),
        str(record.get("Tax_Deduction", 0)),
        str(record.get("Other_Deductions", 0)),
    ]
    return ",".join(values)


def read_records(path=CSV_FILE):
    records = []
    with open(path, "r", encoding="utf-8-sig") as file:
        header = file.readline().strip().split(",")
        for col in REQUIRED_COLUMNS:
            if col not in header:
                raise InvalidPayrollDataError(
                    f"Column '{col}' not found in {os.path.basename(path)}"
                )
        reader = csv.DictReader(file, fieldnames=header)
        line_number = 1
        for row in reader:
            line_number += 1
            emp_id = (row.get("EmpID") or "").strip()
            if emp_id == "":
                continue
            try:
                basic = to_float(row.get("BasicSalary"))
                hra = to_float(row.get("HRA"))
                allowances = to_float(row.get("Allowances"))
                pf = to_float(row.get("PF_Deduction"))
                tax = to_float(row.get("Tax_Deduction"))
                other = to_float(row.get("Other_Deductions"))
                record = analyzer.make_record(
                    emp_id=emp_id,
                    name=(row.get("Name") or "").strip(),
                    department=(row.get("Department") or "").strip(),
                    designation=(row.get("Designation") or "").strip(),
                    gender=(row.get("Gender") or "Unknown").strip(),
                    join_date=(row.get("JoinDate") or "").strip(),
                    pay_month=(row.get("PayMonth") or "").strip(),
                    basic_salary=basic,
                    hra=hra,
                    allowances=allowances,
                    pf_deduction=pf,
                    tax_deduction=tax,
                    other_deductions=other,
                )
            except ValueError:
                print(f"  (skipped bad line {line_number})")
                continue
            records.append(record)
    return records


def count_lines(path=CSV_FILE):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    return len(text.splitlines())


def append_record(record, path=CSV_FILE):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write(HEADER + "\n")
    with open(path, "a", encoding="utf-8") as file:
        file.write(record_to_line(record) + "\n")


def save_all(records, path=CSV_FILE):
    with open(path, "w", encoding="utf-8") as file:
        file.write(HEADER + "\n")
        for record in records:
            file.write(record_to_line(record) + "\n")


def backup_data(records, path=BACKUP_FILE):
    with open(path, "wb") as file:
        pickle.dump(records, file)


def restore_backup(path=BACKUP_FILE):
    with open(path, "rb") as file:
        return pickle.load(file)


def copy_file(source=CSV_FILE, destination=COPY_FILE):
    with open(source, "rb") as src:
        data = src.read()
    with open(destination, "wb") as dst:
        dst.write(data)
    return len(data)


def merge_files(first, second, output=MERGED_FILE):
    for path in (first, second):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
    seen = set()
    written = 0
    with open(output, "w", encoding="utf-8") as out:
        out.write(HEADER + "\n")
        for path in (first, second):
            with open(path, "r", encoding="utf-8") as file:
                file.readline()  # skip header
                for line in file:
                    line = line.strip()
                    if line == "" or line in seen:
                        continue
                    seen.add(line)
                    out.write(line + "\n")
                    written += 1
    return written


def ensure_sample_data():
    """Create the data directory and CSV file if they do not already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_FILE.exists():
        print("Sample payroll data file not found. Please add payroll_data.csv to the data/ folder.")
