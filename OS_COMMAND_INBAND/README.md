# NetProbe Lab — OS Command Injection (In-band, Variant 1)

**Course:** Cyber Security (IT-30001), IIIT Allahabad — Autumn 2026  
**Assignment:** Web Server Security — Exploitation and Mitigation  
**Student:** Rushikesh Dusane  
**Roll number:** IIT2024147  
**Vulnerability category:** OS Command Injection  
**Selected variant:** In-band (command output returned in the HTTP response)

## 1. Project overview

I developed **NetProbe Lab**, a Flask-based network diagnostic application, to demonstrate the exploitation and mitigation of **in-band operating-system command injection**. The application accepts a network target, runs the operating-system `ping` utility, and displays the command output in the browser.

The repository contains two versions of the same application:

- **`Vulnerable_web_app/`** — Builds a shell command from untrusted form input and executes it with `shell=True`. This permits an injected shell separator to execute an additional command.
- **`Secured_web_app/`** — Implements **one mitigation only: strict IPv4 allow-list validation** using Python's `ipaddress.IPv4Address()`. Input that is not a valid IPv4 address is rejected before the command is assembled or executed. The original `shell=True` execution is deliberately retained, making the effect of this single mitigation easy to compare.

Both versions use the same general HTML/CSS interface and the same `/diagnose` endpoint. The main difference is how the backend handles the submitted `target` field.

## 2. Repository structure

The project has **one `README.md` at the repository root** and two independently runnable application folders. 

```text
project-root/
├── README.md
│
├── Secured_web_app/
│   ├── .venv/                    # Local virtual environment (Git-ignored)
│   ├── static/
│   │   ├── app.js
│   │   └── style.css
│   ├── templates/
│   │   └── index.html
│   ├── tests/
│   │   └── test_app.py
│   ├── .gitignore
│   ├── app.py                    # Mitigated backend: IPv4 allow-list
│   ├── demo.txt                  # Local demonstration text file
│   ├── requirements.txt
│   ├── RUN_LINUX_MAC.sh
│   └── RUN_WINDOWS.bat
│
└── Vulnerable_web_app/
    ├── .venv/                    # Local virtual environment (Git-ignored)
    ├── static/
    │   ├── app.js
    │   └── style.css
    ├── templates/
    │   └── index.html
    ├── tests/
    │   └── test_app.py
    ├── .gitignore
    ├── app.py                    # Vulnerable backend: unchecked shell input
    ├── demo.txt                  # Local demonstration text file
    ├── requirements.txt
    ├── RUN_LINUX_MAC.sh
    └── RUN_WINDOWS.bat
```

The `.venv/` directories are generated locally by the launchers and excluded from Git by `.gitignore`. The `demo.txt` files serve as harmless local examples for demonstrating file-reading impact. The remaining source and configuration files are maintained separately for the two versions; there are no additional README files within them.

## 3. Application architecture and HTTP flow

The browser displays an HTML form containing a target address and a **Run diagnostic** button. Submitting the form sends an HTTP `POST` request to Flask. Flask reads the form data and prepares a ping operation. The operating system executes the command, and Flask returns a rendered HTML page containing the result.

```text
Browser (input field)
       |
       | POST /diagnose   target=<submitted input>
       v
Flask app.py -> diagnose()
       |
       | vulnerable folder: unchecked input enters the command
       | allow-list folder: strict IPv4 validation before assembly
       v
make_command() -> execute_unsafe() -> Windows cmd.exe / OS shell
       |
       | stdout, stderr, and exit status
       v
Flask render_template("index.html")
       |
       | HTTP response with command output or validation error
       v
Browser (result displayed on page)
```

On initial page load, the browser requests `/` and the linked `/static/style.css` and `/static/app.js`. Submitting the form calls `POST /diagnose`; the resulting HTML may cause the browser to check the cached CSS and JavaScript again. These static-resource GET requests **do not execute** operating-system commands.

## 4. Main vulnerability and root cause

The vulnerable implementation treats untrusted input as part of an executable shell command. The vulnerability is caused by **two interacting code decisions** in `Vulnerable_web_app/app.py`.

**A. Untrusted input is concatenated into a command string** in `make_command(target)`:

```python
return f"{ping_prefix} {target}"
```

**B. The assembled string is interpreted by a shell** in `execute_unsafe(command)`:

```python
completed = subprocess.run(
    command,
    shell=True,
    text=True,
    capture_output=True,
    timeout=6,
    errors="replace",
)
```

On Windows, the intended command for the normal input `127.0.0.1` is:

```cmd
ping -n 1 -w 1000 127.0.0.1
```

When the input contains `127.0.0.1 & whoami`, the constructed command becomes:

```cmd
ping -n 1 -w 1000 127.0.0.1 & whoami
```

The `&` character is a command separator in Windows `cmd.exe`. The shell interprets the text as **two commands**: the expected `ping`, followed by the unintended `whoami`. The `whoami` command reports the identity of the account running the Flask process.

The application captures `stdout` and `stderr` and renders them in the HTTP response. This makes the vulnerability **in-band**: the output of the injected command is visible directly in the response to the submitted web form. The operating-system command executes **on the server**, not inside the browser.

The flaw is **not** caused by Flask itself or by the use of HTTP POST. It is caused by allowing an untrusted value to influence the syntax of an operating-system shell command. The input length limit, `.strip()`, Flask debug settings, and HTML output escaping do not remove this command-injection vulnerability.

## 5. Exploitation demonstration (local Windows lab)

The application was designed around two comparison requests:

| Test | Submitted `target` | Expected vulnerable behavior |
|---|---|---|
| Normal ping | `127.0.0.1` | Runs ping and displays the diagnostic output |
| In-band injection | `127.0.0.1 & whoami` | Executes ping and `whoami`; displays the additional account-name output |

The vulnerable version's handling of the injection can be summarized as follows:

1. The browser submits the attack string to `POST /diagnose`.
2. Flask retrieves the `target` form value without checking whether it is a valid IP address.
3. `make_command()` appends that value to the ping command.
4. `subprocess.run(..., shell=True)` passes the entire string to the Windows shell.
5. Windows executes the commands separated by `&`.
6. Flask captures the output and returns it in the resulting HTML page (`HTTP 200` when the route completes normally).

A line resembling `COMPUTERNAME\username` after the ping output is evidence that the additional `whoami` command ran. The actual output depends on the account running Flask. An HTTP `200` status alone does **not** prove successful exploitation; the returned command output is the relevant evidence.

For Unix-like operating systems, the example payload is `127.0.0.1; whoami`. The supplied non-Windows ping flags are Linux-oriented; behavior of those flags can vary on macOS. **Windows 11 is the primary target environment for this project.**

## 6. Implemented mitigation — one fix only

The **only implemented security mitigation** in `Secured_web_app/app.py` is **strict input validation with an IPv4 allow-list**.

```python
import ipaddress


def validate_ipv4(target: str) -> str:
    return str(ipaddress.IPv4Address(target))
```

In the `POST /diagnose` handler, input is validated **before** constructing or executing a command:

```python
try:
    validated_ip = validate_ipv4(target)
except ValueError:
    response = {
        "output": "BLOCKED: Input is not a valid IPv4 address. No OS command was executed.",
        "command": "(not assembled — rejected by IPv4 allow-list)",
        "return_code": None,
        "timed_out": False,
        "blocked": True,
        "target": target,
    }
    status_code = 400
else:
    command = make_command(validated_ip)
    response = execute_unsafe(command)
    response["command"] = command
    response["target"] = target
    response["blocked"] = False
    status_code = 200
```

`IPv4Address()` accepts a syntactically valid IPv4 address such as `127.0.0.1`. It rejects shell separators, spaces, extra arguments, hostnames, IPv6 addresses, and invalid IPv4 strings. If validation fails, the application returns **HTTP 400 Bad Request** with a visible blocked-input message. The subprocess function is **not called** for that request.


## 7. Before-and-after behavior

| Input | `Vulnerable_web_app/` | `Secured_web_app/` (IPv4 allow-list) |
|---|---|---|
| `127.0.0.1` | Ping executes; response shown | Ping executes; response shown |
| `127.0.0.1 & whoami` | Additional `whoami` executes; output returned | **Blocked** before command execution; HTTP 400 |
| `127.0.0.1 & dir` | Additional directory-listing command executes | **Blocked** before command execution; HTTP 400 |
| `127.0.0.1 & type demo.txt` | Attempts to display an accessible lab text file | **Blocked** before command execution; HTTP 400 |
| `256.256.256.256` | Passed to ping, which will generally report an address error | **Blocked** as invalid IPv4; HTTP 400 |
| `localhost` | Treated as a hostname and passed to ping | **Blocked**, because only IPv4 literals are accepted |
| `::1` | Passed to ping as an IPv6 literal | **Blocked**, because this implementation permits only IPv4 |

## 8. Additional mitigations (studied, not implemented)

The following defenses are relevant to OS command injection but are **not** implemented in `Secured_web_app/app.py`:

### 8.1 Avoid shell execution

An application should avoid invoking an operating-system shell when the operation can be performed safely through a language library or a dedicated API. Removing the shell removes its interpretation of special characters such as `&`, `;`, and `|` from this operation.

### 8.2 Execute with a fixed argument vector

When launching a command is necessary, the executable and each argument can be passed separately with `shell=False`, instead of combining them into a shell-parsed string. An example for Windows is:

```python
subprocess.run(
    ["ping", "-n", "1", "-w", "1000", validated_ip],
    shell=False,
    capture_output=True,
    text=True,
    timeout=6,
)
```

This approach must still use appropriate input validation, and programs with dangerous argument options require additional restrictions. **This code is an example of an alternative defense; it is not used in this project's one-fix `Secured_web_app/app.py`.**

### 8.3 Apply least privilege

The server should run under a dedicated account with only the permissions required for its task. A restricted account can limit the damage caused by a command-execution vulnerability, but it does not itself prevent injection. This is a defense-in-depth measure.

## 9. Requirements and execution

**Primary environment:** Windows 11, Python 3.10+, and Flask (`requirements.txt`). An Internet connection may be needed for the initial installation of Flask. No database, Docker, Linux VM, Kali Linux, or GPU is required.

Each folder has its own launcher and local `.venv` Python virtual environment. **Both applications use `127.0.0.1:5000`, so only one should be running at a time.**

**Vulnerable version — Windows PowerShell, from the repository root:**

```powershell
cd .\Vulnerable_web_app
.\RUN_WINDOWS.bat
```

**Mitigated version — after stopping the first server with `Ctrl+C`:**

```powershell
cd ..\Secured_web_app
.\RUN_WINDOWS.bat
```

Each `RUN_WINDOWS.bat` is executed from its corresponding folder. Both applications use port 5000, so they are not run simultaneously.

The application URL in either case is:

```text
http://127.0.0.1:5000/
```

The Windows batch script creates `.venv` if needed, installs dependencies from `requirements.txt`, and starts `app.py`. It can also be opened by double-clicking within its folder.

**Linux/macOS:** Each folder includes `RUN_LINUX_MAC.sh`; it launches the corresponding application with `sh RUN_LINUX_MAC.sh`. Shell syntax differs between Windows and Unix-like systems.

## 10. Verification and evidence

Both application folders include unit tests under `tests/test_app.py`. The tests mock `subprocess.run` rather than executing injected commands:

```powershell
cd .\Vulnerable_web_app
.\.venv\Scripts\python.exe -m unittest discover -s tests -v

cd ..\Secured_web_app
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The vulnerable tests check that unchecked input reaches the shell command and that command output is returned in the page. The secured tests check that valid IPv4 input reaches the normal ping path, while injection strings and invalid IP addresses return HTTP 400 **without calling `subprocess.run`**.

The practical evidence for the assignment consists of the following local browser demonstrations:

1. A normal ping request in the vulnerable version.
2. A successful `127.0.0.1 & whoami` injection in the vulnerable version, with command output visible.
3. The identical payload blocked in the secured version, with the validation message and no executed command.

## 11. Ownership declaration

| Member name | Roll number | Category | Variant implemented |
|---|---|---|---|
| Rushikesh Dusane | IIT2024147 | OS command injection | In-band (command output returned) |

**Implementation ownership:** The selected variant, exploitation explanation, and single-mitigation comparison are documented here as the individual contribution for the Web Server Security group assignment. Other group members' contributions are not represented in this repository-level README until their details have been confirmed.
