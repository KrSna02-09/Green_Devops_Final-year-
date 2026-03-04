import customtkinter as ctk
from tkinter import ttk, messagebox

# --- IMPORTS FROM OTHER FILES ---
from database import Database
import visualize

# --- THEME SETTINGS ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Colors
COLOR_BG = "#0F0F0F"        
COLOR_CARD = "#1C1C1C"      
COLOR_ACCENT = "#2CC985"    
COLOR_WARNING = "#F39C12"   
COLOR_DANGER = "#C0392B"    
COLOR_CHART = "#3498DB"

class ExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.db = Database()
        self.editing_id = None 

        # Window Setup
        self.title("Expensio Pro - With Description")
        self.geometry("1200x700") # Made wider to fit description
        self.configure(fg_color=COLOR_BG)

        # Layout: 2 Columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: INPUTS ---
        self.left_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=15)
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="NEW TRANSACTION", font=("Arial", 16, "bold"), text_color="gray").pack(pady=(30, 10))

        self.entry_date = ctk.CTkEntry(self.left_frame, placeholder_text="Date (2025-01-01)", height=40)
        self.entry_date.pack(fill="x", padx=20, pady=5)

        self.entry_cat = ctk.CTkEntry(self.left_frame, placeholder_text="Category (Food)", height=40)
        self.entry_cat.pack(fill="x", padx=20, pady=5)

        self.entry_amt = ctk.CTkEntry(self.left_frame, placeholder_text="Amount (500)", height=40)
        self.entry_amt.pack(fill="x", padx=20, pady=5)

        # NEW: Description Field
        self.entry_desc = ctk.CTkEntry(self.left_frame, placeholder_text="Description (e.g. Lunch with Mom)", height=40)
        self.entry_desc.pack(fill="x", padx=20, pady=5)

        self.btn_action = ctk.CTkButton(self.left_frame, text="+ ADD EXPENSE", height=40, 
                                     fg_color=COLOR_ACCENT, hover_color="#219662", 
                                     font=("Arial", 12, "bold"), command=self.submit_expense)
        self.btn_action.pack(fill="x", padx=20, pady=20)
        
        self.btn_cancel = ctk.CTkButton(self.left_frame, text="Cancel Edit", fg_color="transparent", border_width=1, command=self.reset_form)

        # Budget Section
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(self.left_frame, text="BUDGET CONTROLLER", font=("Arial", 16, "bold"), text_color="gray").pack(pady=(0, 10))
        
        self.entry_budget = ctk.CTkEntry(self.left_frame, placeholder_text="Set Limit (e.g. 2000)", height=40)
        self.entry_budget.pack(fill="x", padx=20, pady=5)
        
        self.btn_budget = ctk.CTkButton(self.left_frame, text="SET LIMIT", height=40,
                                        fg_color="#555", hover_color="#333",
                                        font=("Arial", 12, "bold"), command=self.set_budget)
        self.btn_budget.pack(fill="x", padx=20, pady=10)

        # Theme
        self.theme_menu = ctk.CTkOptionMenu(self.left_frame, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_menu.set("Dark")
        self.theme_menu.pack(side="bottom", pady=20)

        # --- RIGHT PANEL: DASHBOARD ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        # Status Bar
        self.status_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_CARD, corner_radius=10, height=80)
        self.status_frame.pack(fill="x", pady=(0, 15))
        
        self.lbl_total_spent = ctk.CTkLabel(self.status_frame, text="Total Spent: $0", font=("Arial", 18, "bold"))
        self.lbl_total_spent.pack(side="left", padx=20, pady=20)

        self.lbl_budget_status = ctk.CTkLabel(self.status_frame, text="Budget: $0", font=("Arial", 14), text_color="gray")
        self.lbl_budget_status.pack(side="right", padx=20, pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=10)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20), side="bottom")
        self.progress_bar.set(0)

        # Toolbar
        self.top_bar = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.top_bar, text="Recent Transactions", font=("Arial", 22, "bold")).pack(side="left")

        self.btn_chart = ctk.CTkButton(self.top_bar, text="View Chart", fg_color=COLOR_CHART, width=100, command=self.open_chart)
        self.btn_chart.pack(side="right", padx=5)

        self.btn_delete = ctk.CTkButton(self.top_bar, text="Delete Selected", fg_color=COLOR_DANGER, width=120, command=self.delete_expense)
        self.btn_delete.pack(side="right", padx=5)

        self.btn_edit = ctk.CTkButton(self.top_bar, text="Edit", fg_color=COLOR_WARNING, width=80, command=self.load_edit)
        self.btn_edit.pack(side="right", padx=5)

        # Table
        self.table_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_CARD, corner_radius=10)
        self.table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLOR_CARD, foreground="white", fieldbackground=COLOR_CARD, rowheight=35, borderwidth=0, font=("Arial", 11))
        style.configure("Treeview.Heading", background="#2b2b2b", foreground="gray", relief="flat", font=("Arial", 12, "bold"))
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

        # UPDATE: Added "description" to columns
        columns = ("id", "date", "category", "description", "amount")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("id", text="ID"); self.tree.column("id", width=0, stretch="no")
        self.tree.heading("date", text="DATE"); self.tree.column("date", anchor="center", width=100)
        self.tree.heading("category", text="CATEGORY"); self.tree.column("category", anchor="w", width=120) 
        # NEW: Description Column
        self.tree.heading("description", text="DESCRIPTION"); self.tree.column("description", anchor="w", width=250)
        self.tree.heading("amount", text="AMOUNT"); self.tree.column("amount", anchor="e", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_controller_ui()
        self.refresh_list()

    # --- FUNCTIONS ---

    def open_chart(self):
        data = self.db.fetch_category_sums()
        success = visualize.show_category_pie_chart(self, data)
        if not success:
            messagebox.showinfo("Info", "No expenses to show")

    def set_budget(self):
        try:
            val = float(self.entry_budget.get())
            self.db.set_budget(val)
            self.update_controller_ui()
            messagebox.showinfo("Success", f"Budget limit set to ${val}")
            self.entry_budget.delete(0, "end")
        except ValueError:
            messagebox.showerror("Error", "Budget must be a number")

    def update_controller_ui(self):
        total = self.db.get_total_spent()
        limit = self.db.get_budget()
        
        self.lbl_total_spent.configure(text=f"Total Spent: ${total}")
        self.lbl_budget_status.configure(text=f"Limit: ${limit}")

        if limit > 0:
            percent = total / limit
            self.progress_bar.set(min(percent, 1.0))
            if percent < 0.5:
                self.progress_bar.configure(progress_color=COLOR_ACCENT)
                self.lbl_total_spent.configure(text_color=COLOR_ACCENT)
            elif percent < 0.9:
                self.progress_bar.configure(progress_color=COLOR_WARNING)
                self.lbl_total_spent.configure(text_color=COLOR_WARNING)
            else:
                self.progress_bar.configure(progress_color=COLOR_DANGER)
                self.lbl_total_spent.configure(text_color=COLOR_DANGER)
        else:
            self.progress_bar.set(0)

    def submit_expense(self):
        d = self.entry_date.get()
        c = self.entry_cat.get()
        a = self.entry_amt.get()
        desc = self.entry_desc.get() # Get Description

        if not d or not c or not a:
            messagebox.showerror("Error", "Fill Date, Category and Amount")
            return

        try:
            float(a)
            if self.editing_id:
                self.db.update_expense(self.editing_id, d, c, a, desc)
                messagebox.showinfo("Success", "Expense Updated")
            else:
                self.db.add_expense(d, c, a, desc)
            
            self.reset_form()
            self.refresh_list()
            self.update_controller_ui()

        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")

    def load_edit(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select", "Select a row to edit")
            return
        if len(selected_items) > 1:
            messagebox.showwarning("Multiple Selection", "Select only one item to edit")
            return

        selected = selected_items[0]
        vals = self.tree.item(selected)['values']
        self.editing_id = vals[0]

        self.entry_date.delete(0, "end"); self.entry_date.insert(0, vals[1])
        self.entry_cat.delete(0, "end"); self.entry_cat.insert(0, vals[2])
        
        # Load Description (Handle empty description)
        self.entry_desc.delete(0, "end")
        if len(vals) > 3: # Check if description exists in data
             self.entry_desc.insert(0, vals[3])

        amt = str(vals[4]).replace('$', '')
        self.entry_amt.delete(0, "end"); self.entry_amt.insert(0, amt)

        self.btn_action.configure(text="SAVE CHANGES", fg_color=COLOR_WARNING)
        self.btn_cancel.pack(pady=5)

    def reset_form(self):
        self.entry_date.delete(0, "end")
        self.entry_cat.delete(0, "end")
        self.entry_amt.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.editing_id = None
        self.btn_action.configure(text="+ ADD EXPENSE", fg_color=COLOR_ACCENT)
        self.btn_cancel.pack_forget()

    def delete_expense(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select", "Select items to delete")
            return

        count = len(selected_items)
        if messagebox.askyesno("Confirm", f"Delete {count} items?"):
            for item in selected_items:
                item_id = self.tree.item(item)['values'][0]
                self.db.delete_expense(item_id)
            self.refresh_list()
            self.update_controller_ui()
            self.reset_form()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.fetch_all():
            # row: (id, date, cat, amount, desc)
            # Display Order: ID, Date, Cat, Desc, Amount
            display_row = (row[0], row[1], row[2], row[4], f"${row[3]}") 
            self.tree.insert("", "end", values=display_row)

    def change_theme(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        style = ttk.Style()
        if new_mode == "Light":
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            style.configure("Treeview.Heading", background="#ddd", foreground="black")
        else:
            style.configure("Treeview", background=COLOR_CARD, foreground="white", fieldbackground=COLOR_CARD)
            style.configure("Treeview.Heading", background="#2b2b2b", foreground="gray")

if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()