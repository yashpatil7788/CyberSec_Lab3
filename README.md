# Web Server Security: Exploitation and Mitigation

**Indian Institute of Information Technology Allahabad**

**Course:** Cyber Security (IT-30001), Autumn Semester 2026

**Instructor:** Dr. Soumyadev Maity

**Group:** 16

Group assignment demonstrating SQL injection, OS command injection, cross-site scripting (XSS), and cross-site request forgery (CSRF).

> All applications are intentionally vulnerable demo apps. Run them on `localhost` only and test only your own group's applications.

## Video demonstration

Link: https://drive.google.com/drive/folders/1BUni8M-_2mmytMcF7wzSncqZU7KZjfsP

## Team and ownership (Table 3)

| Member | Roll number | Category | Assigned variant |
| --- | --- | --- | --- |
| Kamakshi | IIT2024114 | Cross-Site Scripting (XSS) | Stored XSS |
| Rushikesh | IIT2024147 | OS command injection | In-band |
| Rahul Raut | IIT2024168 | CSRF | GET-based forged action |
| Yash | IIT2024179 | SQL injection | Authentication bypass |
| Arya | IIT2024181 | Cross-Site Scripting (XSS) | Reflected XSS |

## Available projects

| Project | Documentation | Stack | Local URL |
| --- | --- | --- | --- |
| XSS: Stored | [xss-stored/README.md](xss-stored/README.md) |  |  |
| OS command injection | [OS_COMMAND_INBAND/README.md](OS_COMMAND_INBAND/README.md) | Python 3, Flask, HTML5, CSS3, JavaScript, and Jinja2. |  |
| CSRF: GET-based forged action | [CSRF_GET/README.md](CSRF_GET/README.md) | Python, Flask (bank app) and a static attacker page | Bank: http://localhost:5000, attacker: http://localhost:8000 |
| SQL injection: authentication bypass | [sql_injection_auth_bypass](sql_injection_auth_bypass) |  |  |
| XSS: Reflected | [xss_reflected](xss_reflected) | Python 3 with Flask (single-file app, no database). | Home: http://127.0.0.1:5000/ Vulnerable search: http://127.0.0.1:5000/search/vulnerable Mitigated search: http://127.0.0.1:5000/search/safe |

Each project README contains its setup instructions, vulnerable code path, exact exploit, root cause, implemented mitigation, and mitigation theory.
