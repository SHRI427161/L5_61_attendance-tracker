# Lab 5: Static Code Analysis — Issue Report

**Project:** Student Attendance Tracker  
**Tools:** Pylint, Bandit, Flake8

## Overview

The original `attendance_tracker.py` was analyzed using Pylint, Bandit, and Flake8. The findings below document representative problems in the original source and the corresponding fixes made in the cleaned version.

## Issue table

| Issue | Type | Original line(s) | Description | Fix approach |
|---|---|---:|---|---|
| Hard-coded ERP API key | Security — High | 12 | A credential was embedded directly in the source file. | Read the key from the `ERP_API_KEY` environment variable and fail clearly when it is not configured. |
| SSL verification disabled | Security — High | 60 | `verify=False` disables TLS certificate verification and weakens protection against interception. | Use the request library's default certificate verification and specify a finite timeout. |
| Shell command with wildcard | Security — High | 64 | `subprocess.Popen(..., shell=True)` invoked a shell command to archive CSV files. | Replace shell execution with Python's `glob` and `tarfile` modules. |
| Reminder job uses shell | Security — Medium | 69–73 | The job description enabled shell execution for a command string. | Validate a list of command arguments and return the job description with `shell=False`; do not execute a shell command. |
| Mutable default argument | Bug / state leakage | 18 | `register={}` creates a dictionary shared by calls that omit the argument. | Use `None` as the default and initialize the register inside the function. |
| Division by zero | Runtime bug | 23–27 | An empty attendance record list makes `present / total` divide by zero. | Return `0` when no attendance records exist. |
| Incorrect eligibility boundary | Logic error | 29 | `percentage > MIN_ATTENDANCE` incorrectly rejects a student with exactly 75% attendance. | Use `percentage >= MIN_ATTENDANCE`. |
| Duplicate attendance records | Data integrity | 18–20, 81–83 | The original code allowed the same student to be recorded multiple times on the same date. | Validate the student, date, and status, and reject duplicate dates for that student. |
| Inconsistent date format | Input validation | 82 | A date such as `2026-9-3` was accepted despite the expected `YYYY-MM-DD` format. | Parse the date and require the canonical `YYYY-MM-DD` representation. |
| CSV formula injection | Security | 49–55, 77 | A name beginning with a formula character, such as `=`, could be interpreted as a spreadsheet formula. | Prefix potentially dangerous leading formula characters with an apostrophe before exporting the value. |
| Missing HTTP timeout | Reliability | 60 | The ERP request did not set a timeout, so it could wait too long for a response. | Add a finite timeout and call `raise_for_status()` to detect HTTP errors. |
| Obsolete TLS protocol | Security / maintainability | 66–67 | The original code explicitly used `ssl.PROTOCOL_TLSv1`. | Use `ssl.create_default_context()` for secure default TLS settings. |
| Non-standard function names | Code style | Multiple lines | Functions used camelCase rather than Python's conventional `snake_case`. | Rename functions consistently and update their call sites. |
| CSV file resource handling | Maintainability | 49–55 | The file was manually opened and closed without a context manager or explicit encoding. | Use `with open(..., encoding="utf-8", newline="")` to ensure reliable cleanup and encoding. |

## Verification results

The updated source was checked after the fixes:

| Tool | After result |
|---|---|
| Pylint | **10.00/10** |
| Bandit | **No issues identified** |
| Flake8 | **No issues reported** |

The program was also compiled using `python -m py_compile attendance_tracker.py` and executed successfully.

## Conclusion

Static analysis identified security risks, runtime and logic errors, data-integrity problems, and style violations. Addressing these findings improved the readability, reliability, and security of the Student Attendance Tracker.
