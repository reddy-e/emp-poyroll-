"""Custom exceptions for the Employee Payroll System."""


class InvalidPayrollDataError(Exception):
    """Raised when payroll data (employee ID, salary, dates, etc.) is invalid."""
    pass

