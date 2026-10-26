import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "bank.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Customer table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)

    # Account table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_no TEXT PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            pin TEXT NOT NULL,
            balance REAL DEFAULT 0,
            account_type TEXT DEFAULT 'Savings',
            created_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            transaction_date TEXT,
            FOREIGN KEY(account_no) REFERENCES accounts(account_no)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# ACCOUNT NUMBER
# ============================================================

def generate_account_number():
    while True:
        account_no = str(random.randint(1000000000, 9999999999))

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT account_no FROM accounts WHERE account_no=?",
            (account_no,)
        )

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return account_no


# ============================================================
# TRANSACTION FUNCTION
# ============================================================

def add_transaction(account_no, transaction_type, amount, description):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (account_no, transaction_type, amount, description, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        account_no,
        transaction_type,
        amount,
        description,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


# ============================================================
# MAIN APPLICATION
# ============================================================

class BankingSystem:

    def __init__(self, root):

        self.root = root
        self.root.title("Banking Management System")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)

        self.current_account = None

        self.show_home()


    # ========================================================
    # CLEAR WINDOW
    # ========================================================

    def clear_window(self):

        for widget in self.root.winfo_children():
            widget.destroy()


    # ========================================================
    # HOME SCREEN
    # ========================================================

    def show_home(self):

        self.clear_window()

        title = tk.Label(
            self.root,
            text="BANKING MANAGEMENT SYSTEM",
            font=("Arial", 28, "bold")
        )

        title.pack(pady=60)

        subtitle = tk.Label(
            self.root,
            text="Smart Banking • Secure Transactions • Easy Account Management",
            font=("Arial", 13)
        )

        subtitle.pack(pady=10)

        tk.Button(
            self.root,
            text="Create New Account",
            font=("Arial", 14),
            width=25,
            command=self.create_account
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Customer Login",
            font=("Arial", 14),
            width=25,
            command=self.login_screen
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 14),
            width=25,
            command=self.root.destroy
        ).pack(pady=15)


    # ========================================================
    # CREATE ACCOUNT
    # ========================================================

    def create_account(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="CREATE NEW ACCOUNT",
            font=("Arial", 24, "bold")
        ).pack(pady=25)

        frame = tk.Frame(self.root)
        frame.pack()

        labels = [
            "Full Name",
            "Phone Number",
            "Email",
            "Address",
            "PIN",
            "Initial Deposit"
        ]

        entries = {}

        for i, label in enumerate(labels):

            tk.Label(
                frame,
                text=label,
                font=("Arial", 12)
            ).grid(row=i, column=0, padx=15, pady=10, sticky="w")

            entry = tk.Entry(
                frame,
                font=("Arial", 12),
                width=35,
                show="*" if label == "PIN" else ""
            )

            entry.grid(row=i, column=1, padx=15, pady=10)

            entries[label] = entry


        def submit():

            name = entries["Full Name"].get().strip()
            phone = entries["Phone Number"].get().strip()
            email = entries["Email"].get().strip()
            address = entries["Address"].get().strip()
            pin = entries["PIN"].get().strip()
            deposit = entries["Initial Deposit"].get().strip()

            if not name or not phone or not email or not address or not pin:

                messagebox.showerror(
                    "Error",
                    "Please fill all fields."
                )

                return


            if not pin.isdigit() or len(pin) != 4:

                messagebox.showerror(
                    "Error",
                    "PIN must contain exactly 4 digits."
                )

                return


            try:
                deposit = float(deposit)

                if deposit < 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid initial deposit."
                )

                return


            account_no = generate_account_number()

            conn = connect_db()
            cursor = conn.cursor()

            try:

                cursor.execute("""
                    INSERT INTO customers
                    (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, (
                    name,
                    phone,
                    email,
                    address
                ))

                customer_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO accounts
                    (account_no, customer_id, pin, balance,
                     account_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    account_no,
                    customer_id,
                    pin,
                    deposit,
                    "Savings",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

                conn.commit()

                if deposit > 0:

                    cursor.execute("""
                        INSERT INTO transactions
                        (account_no, transaction_type, amount,
                         description, transaction_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        account_no,
                        "Deposit",
                        deposit,
                        "Initial Deposit",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))

                    conn.commit()

                messagebox.showinfo(
                    "Account Created",
                    f"Account created successfully!\n\n"
                    f"Account Number: {account_no}\n"
                    f"Initial Balance: â¹{deposit:.2f}\n\n"
                    f"Please remember your Account Number and PIN."
                )

                self.show_home()

            except Exception as e:

                conn.rollback()

                messagebox.showerror(
                    "Database Error",
                    str(e)
                )

            finally:

                conn.close()


        tk.Button(
            self.root,
            text="Create Account",
            font=("Arial", 13, "bold"),
            width=20,
            command=submit
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 12),
            width=20,
            command=self.show_home
        ).pack()


    # ========================================================
    # LOGIN
    # ========================================================

    def login_screen(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="CUSTOMER LOGIN",
            font=("Arial", 25, "bold")
        ).pack(pady=50)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(
            frame,
            text="Account Number",
            font=("Arial", 13)
        ).grid(row=0, column=0, padx=10, pady=15)

        account_entry = tk.Entry(
            frame,
            font=("Arial", 13),
            width=30
        )

        account_entry.grid(row=0, column=1)


        tk.Label(
            frame,
            text="PIN",
            font=("Arial", 13)
        ).grid(row=1, column=0, padx=10, pady=15)

        pin_entry = tk.Entry(
            frame,
            font=("Arial", 13),
            width=30,
            show="*"
        )

        pin_entry.grid(row=1, column=1)


        def login():

            account_no = account_entry.get().strip()
            pin = pin_entry.get().strip()

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT account_no
                FROM accounts
                WHERE account_no=? AND pin=?
            """, (
                account_no,
                pin
            ))

            result = cursor.fetchone()

            conn.close()

            if result:

                self.current_account = account_no

                self.dashboard()

            else:

                messagebox.showerror(
                    "Login Failed",
                    "Invalid Account Number or PIN."
                )


        tk.Button(
            self.root,
            text="Login",
            font=("Arial", 13, "bold"),
            width=20,
            command=login
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 12),
            width=20,
            command=self.show_home
        ).pack()


    # ========================================================
    # DASHBOARD
    # ========================================================

    def dashboard(self):

        self.clear_window()

        account_no = self.current_account

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.name, a.balance
            FROM customers c
            JOIN accounts a
            ON c.customer_id = a.customer_id
            WHERE a.account_no=?
        """, (account_no,))

        result = cursor.fetchone()

        conn.close()

        if not result:
            self.show_home()
            return

        name, balance = result

        tk.Label(
            self.root,
            text=f"Welcome, {name}",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        tk.Label(
            self.root,
            text=f"Account Number: {account_no}",
            font=("Arial", 13)
        ).pack()

        tk.Label(
            self.root,
            text=f"Current Balance: â¹{balance:.2f}",
            font=("Arial", 18, "bold")
        ).pack(pady=15)


        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)


        buttons = [
            ("Deposit", self.deposit_screen),
            ("Withdraw", self.withdraw_screen),
            ("Transfer Money", self.transfer_screen),
            ("Check Balance", self.check_balance),
            ("Transaction History", self.transaction_history),
            ("Customer Details", self.customer_details),
            ("Analytics", self.analytics),
            ("Logout", self.logout)
        ]


        for i, (text, command) in enumerate(buttons):

            row = i // 2
            col = i % 2

            tk.Button(
                button_frame,
                text=text,
                width=25,
                height=2,
                font=("Arial", 12),
                command=command
            ).grid(
                row=row,
                column=col,
                padx=15,
                pady=10
            )


    # ========================================================
    # DEPOSIT
    # ========================================================

    def deposit_screen(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="DEPOSIT MONEY",
            font=("Arial", 24, "bold")
        ).pack(pady=50)

        tk.Label(
            self.root,
            text="Enter Amount",
            font=("Arial", 13)
        ).pack()

        amount_entry = tk.Entry(
            self.root,
            font=("Arial", 13),
            width=30
        )

        amount_entry.pack(pady=15)


        def deposit():

            try:

                amount = float(amount_entry.get())

                if amount <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid amount."
                )

                return


            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE accounts
                SET balance = balance + ?
                WHERE account_no=?
            """, (
                amount,
                self.current_account
            ))

            conn.commit()
            conn.close()

            add_transaction(
                self.current_account,
                "Deposit",
                amount,
                "Money Deposited"
            )

            messagebox.showinfo(
                "Success",
                f"â¹{amount:.2f} deposited successfully."
            )

            self.dashboard()


        tk.Button(
            self.root,
            text="Deposit",
            width=20,
            font=("Arial", 13),
            command=deposit
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Back",
            width=20,
            font=("Arial", 12),
            command=self.dashboard
        ).pack()


    # ========================================================
    # WITHDRAW
    # ========================================================

    def withdraw_screen(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="WITHDRAW MONEY",
            font=("Arial", 24, "bold")
        ).pack(pady=50)

        tk.Label(
            self.root,
            text="Enter Amount",
            font=("Arial", 13)
        ).pack()

        amount_entry = tk.Entry(
            self.root,
            font=("Arial", 13),
            width=30
        )

        amount_entry.pack(pady=15)


        def withdraw():

            try:

                amount = float(amount_entry.get())

                if amount <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid amount."
                )

                return


            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=?",
                (self.current_account,)
            )

            balance = cursor.fetchone()[0]

            if amount > balance:

                conn.close()

                messagebox.showerror(
                    "Insufficient Balance",
                    "You do not have enough balance."
                )

                return


            cursor.execute("""
                UPDATE accounts
                SET balance = balance - ?
                WHERE account_no=?
            """, (
                amount,
                self.current_account
            ))

            conn.commit()
            conn.close()

            add_transaction(
                self.current_account,
                "Withdrawal",
                amount,
                "Money Withdrawn"
            )

            messagebox.showinfo(
                "Success",
                f"â¹{amount:.2f} withdrawn successfully."
            )

            self.dashboard()


        tk.Button(
            self.root,
            text="Withdraw",
            width=20,
            font=("Arial", 13),
            command=withdraw
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Back",
            width=20,
            font=("Arial", 12),
            command=self.dashboard
        ).pack()


    # ========================================================
    # TRANSFER
    # ========================================================

    def transfer_screen(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="TRANSFER MONEY",
            font=("Arial", 24, "bold")
        ).pack(pady=40)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(
            frame,
            text="Receiver Account Number",
            font=("Arial", 13)
        ).grid(row=0, column=0, padx=10, pady=15)

        receiver_entry = tk.Entry(
            frame,
            font=("Arial", 13),
            width=30
        )

        receiver_entry.grid(row=0, column=1)


        tk.Label(
            frame,
            text="Amount",
            font=("Arial", 13)
        ).grid(row=1, column=0, padx=10, pady=15)

        amount_entry = tk.Entry(
            frame,
            font=("Arial", 13),
            width=30
        )

        amount_entry.grid(row=1, column=1)


        def transfer():

            receiver = receiver_entry.get().strip()

            try:

                amount = float(amount_entry.get())

                if amount <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid amount."
                )

                return


            if receiver == self.current_account:

                messagebox.showerror(
                    "Error",
                    "You cannot transfer money to yourself."
                )

                return


            conn = connect_db()
            cursor = conn.cursor()

            # Check sender balance
            cursor.execute(
                "SELECT balance FROM accounts WHERE account_no=?",
                (self.current_account,)
            )

            sender = cursor.fetchone()

            if sender is None:

                conn.close()

                messagebox.showerror(
                    "Error",
                    "Sender account not found."
                )

                return

            sender_balance = sender[0]


            if amount > sender_balance:

                conn.close()

                messagebox.showerror(
                    "Error",
                    "Insufficient balance."
                )

                return


            # Check receiver
            cursor.execute(
                "SELECT account_no FROM accounts WHERE account_no=?",
                (receiver,)
            )

            receiver_exists = cursor.fetchone()

            if receiver_exists is None:

                conn.close()

                messagebox.showerror(
                    "Error",
                    "Receiver account does not exist."
                )

                return


            # Deduct sender
            cursor.execute("""
                UPDATE accounts
                SET balance = balance - ?
                WHERE account_no=?
            """, (
                amount,
                self.current_account
            ))


            # Add receiver
            cursor.execute("""
                UPDATE accounts
                SET balance = balance + ?
                WHERE account_no=?
            """, (
                amount,
                receiver
            ))


            conn.commit()
            conn.close()


            # Sender transaction
            add_transaction(
                self.current_account,
                "Transfer Sent",
                amount,
                f"Transferred to {receiver}"
            )


            # Receiver transaction
            add_transaction(
                receiver,
                "Transfer Received",
                amount,
                f"Received from {self.current_account}"
            )


            messagebox.showinfo(
                "Success",
                f"â¹{amount:.2f} transferred successfully."
            )

            self.dashboard()


        tk.Button(
            self.root,
            text="Transfer",
            width=20,
            font=("Arial", 13),
            command=transfer
        ).pack(pady=20)


        tk.Button(
            self.root,
            text="Back",
            width=20,
            font=("Arial", 12),
            command=self.dashboard
        ).pack()


    # ========================================================
    # CHECK BALANCE
    # ========================================================

    def check_balance(self):

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT balance FROM accounts WHERE account_no=?",
            (self.current_account,)
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            messagebox.showinfo(
                "Account Balance",
                f"Your current balance is:\n\nâ¹{result[0]:.2f}"
            )


    # ========================================================
    # TRANSACTION HISTORY
    # ========================================================

    def transaction_history(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="TRANSACTION HISTORY",
            font=("Arial", 24, "bold")
        ).pack(pady=25)


        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=20)


        columns = (
            "ID",
            "Type",
            "Amount",
            "Description",
            "Date"
        )


        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=18
        )


        for col in columns:

            tree.heading(
                col,
                text=col
            )

            tree.column(
                col,
                width=150
            )


        tree.pack(
            side="left",
            fill="both",
            expand=True
        )


        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )


        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT transaction_id,
                   transaction_type,
                   amount,
                   description,
                   transaction_date
            FROM transactions
            WHERE account_no=?
            ORDER BY transaction_id DESC
        """, (
            self.current_account,
        ))

        rows = cursor.fetchall()

        conn.close()


        for row in rows:

            tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    row[1],
                    f"â¹{row[2]:.2f}",
                    row[3],
                    row[4]
                )
            )


        tk.Button(
            self.root,
            text="Back",
            width=20,
            font=("Arial", 12),
            command=self.dashboard
        ).pack(pady=20)


    # ========================================================
    # CUSTOMER DETAILS
    # ========================================================

    def customer_details(self):

        self.clear_window()

        tk.Label(
            self.root,
            text="CUSTOMER DETAILS",
            font=("Arial", 24, "bold")
        ).pack(pady=40)


        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.name,
                   c.phone,
                   c.email,
                   c.address,
                   a.account_no,
                   a.account_type,
                   a.balance,
                   a.created_at
            FROM customers c
            JOIN accounts a
            ON c.customer_id = a.customer_id
            WHERE a.account_no=?
        """, (
            self.current_account,
        ))

        data = cursor.fetchone()

        conn.close()


        if data:

            labels = [
                "Name",
                "Phone",
                "Email",
                "Address",
                "Account Number",
                "Account Type",
                "Balance",
                "Created At"
            ]


            frame = tk.Frame(self.root)
            frame.pack()


            for i, (label, value) in enumerate(
                zip(labels, data)
            ):

                tk.Label(
                    frame,
                    text=f"{label}:",
                    font=("Arial", 12, "bold")
                ).grid(
                    row=i,
                    column=0,
                    padx=15,
                    pady=8,
                    sticky="w"
                )


                tk.Label(
                    frame,
                    text=str(value),
                    font=("Arial", 12)
                ).grid(
                    row=i,
                    column=1,
                    padx=15,
                    pady=8,
                    sticky="w"
                )


        tk.Button(
            self.root,
            text="Back",
            width=20,
            font=("Arial", 12),
            command=self.dashboard
        ).pack(pady=30)


    # ========================================================
    # ANALYTICS
    # ========================================================

    def analytics(self):

        conn = connect_db()

        query = """
            SELECT transaction_type,
                   amount,
                   transaction_date
            FROM transactions
            WHERE account_no=?
        """

        df = pd.read_sql_query(
            query,
            conn,
            params=(self.current_account,)
        )

        conn.close()


        if df.empty:

            messagebox.showinfo(
                "Analytics",
                "No transaction data available."
            )

            return


        # NumPy calculations

        total_transactions = len(df)

        total_amount = np.sum(df["amount"])

        average_amount = np.mean(df["amount"])


        deposits = df[
            df["transaction_type"] == "Deposit"
        ]["amount"]

        withdrawals = df[
            df["transaction_type"] == "Withdrawal"
        ]["amount"]


        total_deposit = np.sum(deposits)

        total_withdrawal = np.sum(withdrawals)


        message = (
            f"Total Transactions: {total_transactions}\n\n"
            f"Total Transaction Amount: â¹{total_amount:.2f}\n\n"
            f"Average Transaction: â¹{average_amount:.2f}\n\n"
            f"Total Deposits: â¹{total_deposit:.2f}\n\n"
            f"Total Withdrawals: â¹{total_withdrawal:.2f}"
        )


        messagebox.showinfo(
            "Transaction Analytics",
            message
        )


        # Create graph

        grouped = df.groupby(
            "transaction_type"
        )["amount"].sum()


        plt.figure(
            figsize=(9, 5)
        )

        grouped.plot(
            kind="bar"
        )

        plt.title(
            "Bank Transaction Analysis"
        )

        plt.xlabel(
            "Transaction Type"
        )

        plt.ylabel(
            "Total Amount (â¹)"
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()

        plt.show()


    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        self.current_account = None

        self.show_home()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    create_database()

    root = tk.Tk()

    app = BankingSystem(root)

    root.mainloop()