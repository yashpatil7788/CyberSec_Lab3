require("dotenv").config();

const express = require("express");
const mysql = require("mysql2/promise");
const path = require("path");

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, "public")));

const pool = mysql.createPool({
    host: process.env.DB_HOST || "localhost",
    user: process.env.DB_USER || "root",
    password: process.env.DB_PASSWORD || "",
    database: process.env.DB_NAME || "sqli_lab",
    waitForConnections: true,
    connectionLimit: 5
});

app.post("/api/vulnerable-login", async (req, res) => {
    const { username = "", password = "" } = req.body;

    try {
        const sql = `SELECT id, username FROM users
                     WHERE username = '${username}'
                     AND password = '${password}'`;

        const [rows] = await pool.query(sql);

        if (rows.length > 0) {
            return res.json({
                success: true,
                message: "Login successful",
                user: rows[0].username
            });
        }

        return res.status(401).json({
            success: false,
            message: "Invalid username or password"
        });
    } catch (error) {
        console.error("Vulnerable route database error:", error.message);
        return res.status(500).json({
            success: false,
            message: "Database error. Check the server terminal."
        });
    }
});

app.post("/api/secure-login", async (req, res) => {
    const { username = "", password = "" } = req.body;

    try {
        const sql = `SELECT id, username FROM users
                     WHERE username = ? AND password = ?`;

        const [rows] = await pool.execute(sql, [username, password]);

        if (rows.length > 0) {
            return res.json({
                success: true,
                message: "Login successful",
                user: rows[0].username
            });
        }

        return res.status(401).json({
            success: false,
            message: "Invalid username or password"
        });
    } catch (error) {
        console.error("Secure route database error:", error.message);
        return res.status(500).json({
            success: false,
            message: "Database error. Check the server terminal."
        });
    }
});

app.get("/health", (req, res) => {
    res.json({ status: "ok" });
});

app.listen(PORT, () => {
    console.log(`SQL Injection Lab running at http://localhost:${PORT}`);
});
