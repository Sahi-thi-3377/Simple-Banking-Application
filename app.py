from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "banking.db"

def initialize_database():
    connection = sqlite3.connect(DATABASE)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY,
            balance REAL NOT NULL
        )
    """)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM account")
    if cursor.fetchone()[0] == 0:
        connection.execute("INSERT INTO account (id, balance) VALUES (1, 1000.0)")
    connection.commit()
    connection.close()

def get_balance():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM account WHERE id = 1")
    balance = cursor.fetchone()[0]
    connection.close()
    return balance

@app.route("/")
def home():
    balance = get_balance()
    message = request.args.get("message", "")
    return render_template("index.html", balance=balance, message=message, action_withdraw_enabled=True)

@app.route("/deposit", methods=["POST"])
def deposit():
    amount_str = request.form.get("amount", "0").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            return redirect(url_for("home", message="Invalid deposit amount."))
        
        connection = sqlite3.connect(DATABASE)
        connection.execute("UPDATE account SET balance = balance + ? WHERE id = 1", (amount,))
        connection.commit()
        connection.close()
        return redirect(url_for("home", message=f"Successfully deposited ₹{amount:.2f}!"))
    except ValueError:
        return redirect(url_for("home", message="Invalid input format."))

@app.route("/withdraw", methods=["POST"])
def withdraw():
    amount_str = request.form.get("w_amount", "0").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            return redirect(url_for("home", message="Invalid withdrawal amount."))
        
        current_balance = get_balance()
        if amount > current_balance:
            return redirect(url_for("home", message="Transaction failed: Insufficient balance!"))
            
        connection = sqlite3.connect(DATABASE)
        connection.execute("UPDATE account SET balance = balance - ? WHERE id = 1", (amount,))
        connection.commit()
        connection.close()
        return redirect(url_for("home", message=f"Successfully withdrew ₹{amount:.2f}!"))
    except ValueError:
        return redirect(url_for("home", message="Invalid input format."))

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)