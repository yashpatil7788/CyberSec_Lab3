# SQL Injection – Authentication Bypass Lab

A small local-only teaching application with two login endpoints:
- **Vulnerable:** concatenates form input into SQL.
- **Secured:** uses parameterized SQL with placeholders.

The website contains only the demonstration interface. The separate `docs/` folder contains the written solution guide and viva preparation.

## Requirements

- Node.js 18+
- MySQL Server

## Setup

1. Create a MySQL database and demo user table by running `database.sql` in MySQL Workbench or the MySQL command line.
2. Copy `.env.example` to `.env`.
3. Update the MySQL username and password in `.env`.
4. Install dependencies:

   ```bash
   npm install
   ```

5. Start the application:

   ```bash
   npm start
   ```

6. Open `http://localhost:3000`.

## Test

Normal account:
- Username: `admin`
- Password: `admin123`

First verify that a wrong password fails. Then use the SQL injection test payload described in `docs/solution-guide.md` on the vulnerable form and repeat the same test on the secured form.

## Important

This intentionally vulnerable endpoint is for a local, isolated classroom demonstration only. Do not deploy it to a public server or use it against systems you do not own or have explicit permission to test.

The demo uses a plaintext dummy password to keep the SQL injection concept visible and simple. It is not a production authentication design. Real applications should store password hashes (for example, Argon2id or bcrypt), use parameterized queries, apply least privilege, and return generic authentication errors.
