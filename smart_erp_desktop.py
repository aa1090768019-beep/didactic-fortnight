# Complete working code for smart_erp_desktop.py

import tkinter as tk
from tkinter import ttk

class SmartERP:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart ERP Desktop")
        self.root.geometry("600x400")

        # Create label
        self.label = ttk.Label(self.root, text="Welcome to Smart ERP!", font=("Arial", 16))
        self.label.pack(pady=20)

        # Create buttons
        self.add_button = ttk.Button(self.root, text="Add Record", command=self.add_record)
        self.add_button.pack(pady=10)

        self.view_button = ttk.Button(self.root, text="View Records", command=self.view_records)
        self.view_button.pack(pady=10)

        self.exit_button = ttk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=10)

    def add_record(self):
        print("Add Record Button Clicked")

    def view_records(self):
        print("View Records Button Clicked")

if __name__ == '__main__':
    root = tk.Tk()
    app = SmartERP(root)
    root.mainloop()