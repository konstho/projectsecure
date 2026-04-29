# Applied Web Application Security Course Project

A small intentionally vulnerable shop web application built with Flask for educational purposes. The project demonstrates common web application security flaws in a practical environment.

## Vulnerabilities Included

**SQL Injection**
Search functionality is vulnerable to SQL injection, allowing extraction of usernames and passwords from the database.

**Stored XSS / Session Hijacking**
Product reviews allow stored JavaScript payloads that can steal user session cookies and enable account hijacking.

**IDOR**
Order pages are vulnerable to insecure direct object references, allowing users to access other users’ order information by modifying the URL.

## Tech Stack

Python, Flask, SQLite, HTML/CSS, JavaScript

**Note:** This application is intentionally vulnerable and created strictly for educational purposes.
