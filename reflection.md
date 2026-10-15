# Lab 5: Static Code Analysis — Reflection

> The supplied three-page handout does not list specific reflection questions. This document is therefore a general reflection on the lab, not a set of answers to instructor-provided questions.

## What I learned

I learned that static code analysis checks source code for potential problems without needing to execute it. It helps identify issues early, before they cause failures or security problems.

## Tools and their purposes

- **Pylint** checks code quality, naming conventions, and common programming mistakes.
- **Bandit** identifies common security risks and unsafe coding patterns in Python.
- **Flake8** checks Python style and formatting issues.

Using the three tools together provides different but complementary views of the same code.

## Issues I corrected

The original program contained a hard-coded ERP API key, disabled TLS certificate verification, unsafe shell execution, a mutable default argument, a possible division-by-zero error, an incorrect 75% eligibility condition, duplicate attendance entries, and inconsistent date formatting.

I changed the code to use an environment variable for the API key, retain TLS verification, avoid shell-based archiving, handle empty records, validate attendance input, reject duplicate records, and use consistent naming and file handling.

## Verification and outcome

After the changes, the results I observed were:

- Pylint: **10.00/10**
- Bandit: **No issues identified**
- Flake8: **No issues reported**

I also ran `python -m py_compile attendance_tracker.py` and executed the program to check that it worked.

## Conclusion

This lab showed me that static analysis is useful for improving security, correctness, and maintainability. I learned that a clean tool report is an important check, but it does not prove that a program has no possible bugs. Running the program and testing its behavior are still necessary.
