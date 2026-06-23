import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import os

class ATMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Start hidden until splash screen done
        self.title("ATM Management System")
        self.geometry("900x600")
        self.minsize(600, 400)
        self.resizable(True, True)
        self.current_user = None

        # Initialize SQLite database
        self.conn = sqlite3.connect("atm_transactions.db")
        self.create_tables()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginScreen, RegisterScreen, HomeScreen, DepositScreen, WithdrawScreen, CheckBalanceScreen, TransactionHistoryScreen, UserDetailsScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_splash_screen()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                fullname TEXT NOT NULL,
                nationality TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                dob TEXT NOT NULL,
                balance REAL NOT NULL
            )
        ''')
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password, fullname, nationality, address, phone, email, dob):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password, fullname, nationality, address, phone, email, dob, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0)
            ''', (username, password, fullname, nationality, address, phone, email, dob))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        if not result:
            return False, "Account does not exist."
        return (True, "") if result[0] == password else (False, "Incorrect password.")

    def get_user_details(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT fullname, nationality, address, phone, email, dob, balance FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

    def add_transaction(self, username, transaction_type, amount):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO transactions (username, transaction_type, amount, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (username, transaction_type, amount, timestamp))
        self.conn.commit()

    def get_transactions(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, transaction_type, amount, timestamp FROM transactions WHERE username = ?', (username,))
        return cursor.fetchall()

    def update_balance(self, username, amount, is_deposit=True):
        cursor = self.conn.cursor()
        if is_deposit:
            cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, username))
        else:
            cursor.execute('UPDATE users SET balance = balance - ? WHERE username = ?', (amount, username))
        self.conn.commit()

    def show_splash_screen(self):
        splash = SplashScreen(self, self.after_splash)
        splash.grab_set()

    def after_splash(self):
        self.deiconify()
        self.show_frame(LoginScreen)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, on_close_callback):
        super().__init__(parent)
        self.title("Welcome")
        self.geometry("900x550")
        self.resizable(True, True)

        try:
            self.bg_image_path = "D:/AI-Labs/HCI &CG project/online-banking.jpg"
            self.original_img = Image.open(self.bg_image_path)
            self.bg = ImageTk.PhotoImage(self.original_img)
            self.bg_label = tk.Label(self, image=self.bg)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Image load error:", e)

        self.banner = tk.Frame(self, bg="white", height=70)
        self.banner.place(relx=0, rely=0, relwidth=1)
        self.banner.pack_propagate(False)

        self.title_label = tk.Label(self.banner, text="ATM MANAGEMENT SYSTEM", font=("Verdana", 28, "bold"),
                                   fg="#1e121e", bg="white")
        self.title_label.pack(expand=True)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.place(relx=0.5, rely=0.95, anchor="center")
        self.progress["maximum"] = 100
        self.current_progress = 0

        self.on_close_callback = on_close_callback
        self.update_progress()
        self.bind("<Configure>", self.on_resize)

    def update_progress(self):
        if self.current_progress < 100:
            self.current_progress += 2
            self.progress["value"] = self.current_progress
            self.after(100, self.update_progress)
        else:
            self.close_splash()

    def on_resize(self, event):
        try:
            resized_img = self.original_img.resize((event.width, event.height))
            self.bg = ImageTk.PhotoImage(resized_img)
            self.bg_label.config(image=self.bg)
        except:
            pass

    def close_splash(self):
        self.destroy()
        self.on_close_callback()

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        try:
            self.bg_path = "D:/AI-Labs/HCI &CG project/login screen.png"
            self.original_bg = Image.open(self.bg_path)
            self.bg = ImageTk.PhotoImage(self.original_bg)
            self.bg_label = tk.Label(self, image=self.bg)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.bind("<Configure>", self.resize_background)
        except Exception as e:
            print("Image load error:", e)

        self.content_frame = tk.Frame(self, bg='#f5f5f5')
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center", width=380, height=350)

        tk.Label(self.content_frame, text="ATM Management System",
                font=("Arial", 20, "bold"), fg="#2c3e50", bg='#f5f5f5',
                pady=10).pack()

        tk.Label(self.content_frame, text="Welcome to ATM System",
                font=("Arial", 14), fg="#2c3e50", bg='#f5f5f5',
                pady=5).pack()

        input_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Username", font=("Arial", 12),
                fg="#2c3e50", bg='#f5f5f5').grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.username_entry = tk.Entry(input_frame, font=("Arial", 12),
                                     width=25, bd=2, relief=tk.GROOVE,
                                     bg='white', highlightbackground="#bdc3c7")
        self.username_entry.grid(row=1, column=0, pady=(0, 15), ipady=5)

        tk.Label(input_frame, text="Password", font=("Arial", 12),
                fg="#2c3e50", bg='#f5f5f5').grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.password_entry = tk.Entry(input_frame, font=("Arial", 12), show="*",
                                     width=25, bd=2, relief=tk.GROOVE,
                                     bg='white', highlightbackground="#bdc3c7")
        self.password_entry.grid(row=3, column=0, pady=(0, 20), ipady=5)

        button_frame = tk.Frame(self.content_frame, bg='#f5f5f5')
        button_frame.pack(pady=10)

        login_btn = tk.Button(button_frame, text="Login", font=("Arial", 12, "bold"),
                             bg="#3498db", fg="white", width=10, height=1, bd=0,
                             activebackground="#2980b9", activeforeground="white",
                             command=self.login)
        login_btn.grid(row=0, column=0, padx=10, pady=5)

        register_btn = tk.Button(button_frame, text="Register", font=("Arial", 12, "bold"),
                                bg="#2ecc71", fg="white", width=10, height=1, bd=0,
                                activebackground="#27ae60", activeforeground="white",
                                command=lambda: controller.show_frame(RegisterScreen))
        register_btn.grid(row=0, column=1, padx=10, pady=5)

        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#2980b9"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#3498db"))
        register_btn.bind("<Enter>", lambda e: register_btn.config(bg="#27ae60"))
        register_btn.bind("<Leave>", lambda e: register_btn.config(bg="#2ecc71"))

    def resize_background(self, event):
        try:
            resized = self.original_bg.resize((event.width, event.height))
            self.bg = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg)
        except:
            pass

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            messagebox.showerror("Error", "Please enter your username.")
            return

        if not password:
            messagebox.showerror("Error", "Please enter your password.")
            return

        success, msg = self.controller.login_user(username, password)
        if success:
            self.controller.current_user = username
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.controller.show_frame(HomeScreen)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Login Failed", msg)

class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="Register New Account", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        outer_frame = tk.Frame(self, bg="#1e272e")
        outer_frame.pack(pady=10, padx=30, fill='both', expand=True)

        left_frame = tk.Frame(outer_frame, bg="#1e272e")
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        right_frame = tk.Frame(outer_frame, bg="#1e272e")
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        self.fullname_entry = self.create_entry(left_frame, "Full Name")
        self.username_entry = self.create_entry(left_frame, "Username")
        self.password_entry = self.create_entry(left_frame, "Password", show="*")
        self.confirm_password_entry = self.create_entry(left_frame, "Confirm Password")

        self.nationality_var = tk.StringVar()
        tk.Label(right_frame, text="Nationality", font=("Arial", 14), bg="#1e272e", fg="white").pack(anchor="w")

        countries = [
            "Pakistani", "India", "United States", "United Kingdom", "Canada", "Australia",
            "Germany", "France", "China", "Japan", "Brazil", "Russia", "South Africa"
        ]

        self.nationality_combo = ttk.Combobox(
            right_frame,
            textvariable=self.nationality_var,
            values=countries,
            state="readonly",
            font=("Arial", 12),
            width=30
        )
        self.nationality_combo.pack(pady=5, ipady=6)

        self.address_entry = self.create_entry(right_frame, "Address")
        self.phone_entry = self.create_entry(right_frame, "Phone Number")
        self.email_entry = self.create_entry(right_frame, "Email Address")

        tk.Label(right_frame, text="Date of Birth", font=("Arial", 14), bg="#1e272e", fg="white").pack(pady=(10, 0))
        dob_frame = tk.Frame(right_frame, bg="#1e272e")
        dob_frame.pack(pady=5)

        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()

        days = [str(d) for d in range(1, 32)]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        years = [str(y) for y in range(1950, 2026)]

        ttk.Combobox(dob_frame, textvariable=self.day_var, values=days, width=5, font=("Arial", 12), state="readonly").grid(row=0, column=0, padx=2)
        ttk.Combobox(dob_frame, textvariable=self.month_var, values=months, width=7, font=("Arial", 12), state="readonly").grid(row=0, column=1, padx=2)
        ttk.Combobox(dob_frame, textvariable=self.year_var, values=years, width=7, font=("Arial", 12), state="readonly").grid(row=0, column=2, padx=2)

        button_frame = tk.Frame(self, bg="#1e272e")
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Back to Login", font=("Arial", 12, "bold"), bg="#fc5c65", fg="white",
                  width=15, height=2, command=lambda: controller.show_frame(LoginScreen)).grid(row=0, column=0, padx=20)
        tk.Button(button_frame, text="Register", font=("Arial", 12, "bold"), bg="#20bf6b", fg="white",
                  width=15, height=2, command=self.register).grid(row=0, column=1, padx=20)

    def create_entry(self, parent, placeholder, show=None):
        tk.Label(parent, text=placeholder, font=("Arial", 14), bg="#1e272e", fg="white").pack(anchor="w", pady=(10, 0))
        entry = tk.Entry(parent, font=("Arial", 12), show=show, width=30)
        entry.pack(pady=5, ipady=6)
        return entry

    def register(self):
        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        nationality = self.nationality_var.get()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        day = self.day_var.get()
        month = self.month_var.get()
        year = self.year_var.get()

        if not fullname or not username or not password or not confirm_password or not nationality or not address or not phone or not email or not day or not month or not year:
            messagebox.showerror("Error", "All fields are required.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        dob = f"{day}-{month}-{year}"
        if self.controller.register_user(username, password, fullname, nationality, address, phone, email, dob):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.controller.show_frame(LoginScreen)
            self.fullname_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
            self.nationality_combo.set("")
            self.address_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.day_var.set("")
            self.month_var.set("")
            self.year_var.set("")
        else:
            messagebox.showerror("Error", "Username already exists.")

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="ATM Management System", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        content_frame = tk.Frame(self, bg="#1e272e")
        content_frame.pack(pady=20, padx=30, fill='both', expand=True)

        button_frame = tk.Frame(content_frame, bg="#1e272e")
        button_frame.pack(pady=20)

        deposit_btn = tk.Button(button_frame, text="Deposit", font=("Arial", 12, "bold"),
                               bg="#3498db", fg="white", width=15, height=2, bd=0,
                               activebackground="#2980b9", activeforeground="white",
                               command=lambda: controller.show_frame(DepositScreen))
        deposit_btn.grid(row=0, column=0, padx=10, pady=10)

        check_balance_btn = tk.Button(button_frame, text="Check Balance", font=("Arial", 12, "bold"),
                                     bg="#3498db", fg="white", width=15, height=2, bd=0,
                                     activebackground="#2980b9", activeforeground="white",
                                     command=lambda: controller.show_frame(CheckBalanceScreen))
        check_balance_btn.grid(row=0, column=1, padx=10, pady=10)

        withdraw_btn = tk.Button(button_frame, text="Withdraw", font=("Arial", 12, "bold"),
                                bg="#3498db", fg="white", width=15, height=2, bd=0,
                                activebackground="#2980b9", activeforeground="white",
                                command=lambda: controller.show_frame(WithdrawScreen))
        withdraw_btn.grid(row=1, column=0, padx=10, pady=10)

        history_btn = tk.Button(button_frame, text="Transaction History", font=("Arial", 12, "bold"),
                               bg="#3498db", fg="white", width=15, height=2, bd=0,
                               activebackground="#2980b9", activeforeground="white",
                               command=lambda: controller.show_frame(TransactionHistoryScreen))
        history_btn.grid(row=1, column=1, padx=10, pady=10)

        logout_btn = tk.Button(button_frame, text="Logout", font=("Arial", 12, "bold"),
                              bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                              activebackground="#eb4d55", activeforeground="white",
                              command=self.logout)
        logout_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=20)

        deposit_btn.bind("<Enter>", lambda e: deposit_btn.config(bg="#2980b9"))
        deposit_btn.bind("<Leave>", lambda e: deposit_btn.config(bg="#3498db"))
        check_balance_btn.bind("<Enter>", lambda e: check_balance_btn.config(bg="#2980b9"))
        check_balance_btn.bind("<Leave>", lambda e: check_balance_btn.config(bg="#3498db"))
        withdraw_btn.bind("<Enter>", lambda e: withdraw_btn.config(bg="#2980b9"))
        withdraw_btn.bind("<Leave>", lambda e: withdraw_btn.config(bg="#3498db"))
        history_btn.bind("<Enter>", lambda e: history_btn.config(bg="#2980b9"))
        history_btn.bind("<Leave>", lambda e: history_btn.config(bg="#3498db"))
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg="#eb4d55"))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        self.welcome_label.config(text=f"Welcome, {username}!")

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginScreen)

class DepositScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="Deposit", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        content_frame = tk.Frame(self, bg="#1e272e")
        content_frame.pack(pady=20, padx=30, fill='both', expand=True)

        tk.Label(content_frame, text="Enter Deposit Amount", font=("Arial", 14), fg="white", bg="#1e272e").pack(anchor="w", pady=(10, 0))
        self.amount_entry = tk.Entry(content_frame, font=("Arial", 12), width=30)
        self.amount_entry.pack(pady=5, ipady=6)

        button_frame = tk.Frame(content_frame, bg="#1e272e")
        button_frame.pack(pady=20)

        submit_btn = tk.Button(button_frame, text="Submit", font=("Arial", 12, "bold"),
                              bg="#20bf6b", fg="white", width=15, height=2, bd=0,
                              activebackground="#27ae60", activeforeground="white",
                              command=self.submit_deposit)
        submit_btn.grid(row=0, column=0, padx=10, pady=10)

        back_btn = tk.Button(button_frame, text="Back to Home", font=("Arial", 12, "bold"),
                             bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                             activebackground="#eb4d55", activeforeground="white",
                             command=lambda: controller.show_frame(HomeScreen))
        back_btn.grid(row=0, column=1, padx=10, pady=10)

        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg="#27ae60"))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#20bf6b"))
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#eb4d55"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        details = self.controller.get_user_details(username)
        if details:
            balance = details[6]
            self.welcome_label.config(text=f"Current Balance: {balance:.2f}")
        self.amount_entry.delete(0, tk.END)

    def submit_deposit(self):
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be positive.")
                return
            username = self.controller.current_user
            self.controller.update_balance(username, amount, is_deposit=True)
            self.controller.add_transaction(username, "Deposit", amount)
            messagebox.showinfo("Success", f"Deposited {amount:.2f} successfully!")
            self.controller.show_frame(HomeScreen)
            self.amount_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

class WithdrawScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="Withdraw", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        content_frame = tk.Frame(self, bg="#1e272e")
        content_frame.pack(pady=20, padx=30, fill='both', expand=True)

        tk.Label(content_frame, text="Enter Withdrawal Amount", font=("Arial", 14), fg="white", bg="#1e272e").pack(anchor="w", pady=(10, 0))
        self.amount_entry = tk.Entry(content_frame, font=("Arial", 12), width=30)
        self.amount_entry.pack(pady=5, ipady=6)

        button_frame = tk.Frame(content_frame, bg="#1e272e")
        button_frame.pack(pady=20)

        submit_btn = tk.Button(button_frame, text="Submit", font=("Arial", 12, "bold"),
                              bg="#20bf6b", fg="white", width=15, height=2, bd=0,
                              activebackground="#27ae60", activeforeground="white",
                              command=self.submit_withdraw)
        submit_btn.grid(row=0, column=0, padx=10, pady=10)

        back_btn = tk.Button(button_frame, text="Back to Home", font=("Arial", 12, "bold"),
                            bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                            activebackground="#eb4d55", activeforeground="white",
                            command=lambda: controller.show_frame(HomeScreen))
        back_btn.grid(row=0, column=1, padx=10, pady=10)

        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg="#27ae60"))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#20bf6b"))
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#eb4d55"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        details = self.controller.get_user_details(username)
        if details:
            balance = details[6]
            self.welcome_label.config(text=f"Current Balance: {balance:.2f}")
        self.amount_entry.delete(0, tk.END)

    def submit_withdraw(self):
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be positive.")
                return
            username = self.controller.current_user
            details = self.controller.get_user_details(username)
            if not details:
                messagebox.showerror("Error", "User not found.")
                return
            current_balance = details[6]
            if amount > current_balance:
                messagebox.showerror("Error", "Insufficient balance.")
                return
            self.controller.update_balance(username, amount, is_deposit=False)
            self.controller.add_transaction(username, "Withdraw", amount)
            messagebox.showinfo("Success", f"Withdrew {amount:.2f} successfully!")
            self.controller.show_frame(HomeScreen)
            self.amount_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

class CheckBalanceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="Check Balance", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        self.balance_label = tk.Label(self, text="", font=("Arial", 14), fg="white", bg="#1e272e")
        self.balance_label.pack(pady=20)

        button_frame = tk.Frame(self, bg="#1e272e")
        button_frame.pack(pady=20)

        back_btn = tk.Button(button_frame, text="Back to Home", font=("Arial", 12, "bold"),
                             bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                             activebackground="#eb4d55", activeforeground="white",
                             command=lambda: controller.show_frame(HomeScreen))
        back_btn.pack(pady=10)

        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#eb4d55"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        self.welcome_label.config(text=f"Balance for {username}")
        details = self.controller.get_user_details(username)
        if details:
            balance = details[6]
            self.balance_label.config(text=f"Current Balance: {balance:.2f}")

class TransactionHistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="Transaction History", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        columns = ("ID", "Type", "Amount", "Date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("ID", text="Transaction ID")
        self.tree.heading("Type", text="Transaction Type")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Date", text="Date")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Type", width=150, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Date", width=200, anchor="center")
        self.tree.pack(pady=20, padx=30, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        button_frame = tk.Frame(self, bg="#1e272e")
        button_frame.pack(pady=20)

        back_btn = tk.Button(button_frame, text="Back to Home", font=("Arial", 12, "bold"),
                             bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                             activebackground="#eb4d55", activeforeground="white",
                             command=lambda: controller.show_frame(HomeScreen))
        back_btn.pack(pady=10)

        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#eb4d55"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        transactions = self.controller.get_transactions(username)
        for trans in transactions:
            self.tree.insert("", "end", values=trans)

class UserDetailsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller

        tk.Label(self, text="User Details", font=("Helvetica", 20, "bold"),
                 fg="#00e6e6", bg="#1e272e").pack(pady=20)

        self.welcome_label = tk.Label(self, text="", font=("Arial", 16), fg="white", bg="#1e272e")
        self.welcome_label.pack(pady=10)

        self.details_frame = tk.Frame(self, bg="#1e272e")
        self.details_frame.pack(pady=20, padx=30, fill="x")

        self.fullname_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.fullname_label.pack(anchor="w")
        self.nationality_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.nationality_label.pack(anchor="w")
        self.address_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.address_label.pack(anchor="w")
        self.phone_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.phone_label.pack(anchor="w")
        self.email_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.email_label.pack(anchor="w")
        self.dob_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.dob_label.pack(anchor="w")
        self.balance_label = tk.Label(self.details_frame, text="", font=("Arial", 12), fg="white", bg="#1e272e")
        self.balance_label.pack(anchor="w")

        button_frame = tk.Frame(self, bg="#1e272e")
        button_frame.pack(pady=20)

        back_btn = tk.Button(button_frame, text="Back to Home", font=("Arial", 12, "bold"),
                             bg="#fc5c65", fg="white", width=15, height=2, bd=0,
                             activebackground="#eb4d55", activeforeground="white",
                             command=lambda: controller.show_frame(HomeScreen))
        back_btn.pack(pady=10)

        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#eb4d55"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#fc5c65"))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        username = self.controller.current_user
        self.welcome_label.config(text=f"Details for {username}")
        details = self.controller.get_user_details(username)
        if details:
            fullname, nationality, address, phone, email, dob, balance = details
            self.fullname_label.config(text=f"Full Name: {fullname}")
            self.nationality_label.config(text=f"Nationality: {nationality}")
            self.address_label.config(text=f"Address: {address}")
            self.phone_label.config(text=f"Phone: {phone}")
            self.email_label.config(text=f"Email: {email}")
            self.dob_label.config(text=f"Date of Birth: {dob}")
            self.balance_label.config(text=f"Balance: {balance:.2f}")

if __name__ == "__main__":
    app = ATMApp()
    app.withdraw()
    app.mainloop()