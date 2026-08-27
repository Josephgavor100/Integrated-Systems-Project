import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from gridcare_lite.database import init_db, verify_user, fetch_all_outages, add_outage

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GridCareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GridCare-Lite | National Grid Operational Dashboard")
        self.geometry("1000x650")
        self.minsize(900, 550)

        init_db()
        self.current_user = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_login_view()

    def show_login_view(self):
        login_frame = LoginFrame(parent=self.container, controller=self)
        login_frame.grid(row=0, column=0, sticky="nsew")
        login_frame.tkraise()

    def show_dashboard_view(self, user_info):
        self.current_user = user_info
        dashboard_frame = DashboardFrame(parent=self.container, controller=self, user=user_info)
        dashboard_frame.grid(row=0, column=0, sticky="nsew")
        dashboard_frame.tkraise()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        card = ctk.CTkFrame(self, corner_radius=15, width=380, height=480)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="⚡ GridCare-Lite", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(25, 5))
        ctk.CTkLabel(card, text="National Grid Utility Portal", text_color="gray").pack(pady=(0, 15))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Password", show="•", width=280, height=40)
        self.password_entry.pack(pady=8)

        # Theme Selector Dropdown on Login Screen
        self.theme_menu = ctk.CTkOptionMenu(
            card,
            values=["Dark", "Light", "System"],
            width=280,
            height=35,
            command=lambda mode: ctk.set_appearance_mode(mode)
        )
        self.theme_menu.set(ctk.get_appearance_mode())
        self.theme_menu.pack(pady=8)

        ctk.CTkButton(card, text="Sign In", width=280, height=40, command=self.handle_login).pack(pady=15)
        self.status_label = ctk.CTkLabel(card, text="", text_color="#ff5555")
        self.status_label.pack(pady=5)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user = verify_user(username, password)
        if user:
            self.status_label.configure(text="")
            self.controller.show_dashboard_view(user)
        else:
            self.status_label.configure(text="Invalid credentials (Try: admin / admin123)")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, user):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="⚡ GridCare", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(sidebar, text=f"User: {user['username']}\nRole: {user['role']}", text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=(0, 20))

        ctk.CTkButton(sidebar, text="Dashboard & Logs", width=160, command=self.render_logs_view).pack(pady=10)
        ctk.CTkButton(sidebar, text="Analytics Chart", width=160, command=self.render_chart_view).pack(pady=10)
        
        # Appearance Mode Selector
        ctk.CTkLabel(sidebar, text="Appearance Mode:", font=ctk.CTkFont(size=12), text_color="gray").pack(side="bottom", pady=(0, 2))
        self.theme_menu = ctk.CTkOptionMenu(
            sidebar, 
            values=["Dark", "Light", "System"], 
            width=160, 
            command=self.change_appearance_mode
        )
        self.theme_menu.set(ctk.get_appearance_mode())
        self.theme_menu.pack(side="bottom", pady=(0, 15))

        ctk.CTkButton(sidebar, text="Logout", fg_color="#d32f2f", hover_color="#9a0007", width=160, command=lambda: controller.show_login_view()).pack(side="bottom", pady=(0, 15))

        # Main View Area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.render_logs_view()

    def change_appearance_mode(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)
        # Update treeview style colors depending on mode
        self.update_treeview_theme(new_mode)
        # If currently on the chart view, re-render to update figure colors
        if hasattr(self, 'current_view') and self.current_view == 'chart':
            self.render_chart_view()

    def update_treeview_theme(self, mode: str):
        style = ttk.Style()
        style.theme_use("clam")
        if mode == "Light":
            style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff", rowheight=25)
            style.map("Treeview", background=[("selected", "#3b8ed0")])
        else:
            style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=25)
            style.map("Treeview", background=[("selected", "#1f538d")])

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def render_logs_view(self):
        self.current_view = 'logs'
        self.clear_main_area()

        ctk.CTkLabel(self.main_area, text="Outage Management & Operations", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 15))

        # Form Section
        form_frame = ctk.CTkFrame(self.main_area)
        form_frame.pack(fill="x", pady=(0, 15), padx=5, ipady=5)

        self.reg_entry = ctk.CTkEntry(form_frame, placeholder_text="Region", width=140)
        self.reg_entry.grid(row=0, column=0, padx=5, pady=5)

        self.sev_option = ctk.CTkOptionMenu(form_frame, values=["Low", "Medium", "High", "Critical"], width=130)
        self.sev_option.grid(row=0, column=1, padx=5, pady=5)

        self.stat_option = ctk.CTkOptionMenu(form_frame, values=["Active", "Investigating", "Resolved"], width=130)
        self.stat_option.grid(row=0, column=2, padx=5, pady=5)

        self.desc_entry = ctk.CTkEntry(form_frame, placeholder_text="Description", width=220)
        self.desc_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(form_frame, text="Log Outage", width=110, command=self.handle_add_outage).grid(row=0, column=4, padx=5, pady=5)

        # Table Display Section
        table_frame = ctk.CTkFrame(self.main_area)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ("ID", "Region", "Severity", "Status", "Description", "Timestamp")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.update_treeview_theme(ctk.get_appearance_mode())

        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110 if col != "Description" else 200)

        self.tree.pack(fill="both", expand=True)
        self.load_tree_data()

    def load_tree_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in fetch_all_outages():
            self.tree.insert("", "end", values=row)

    def handle_add_outage(self):
        region = self.reg_entry.get().strip()
        severity = self.sev_option.get()
        status = self.stat_option.get()
        desc = self.desc_entry.get().strip()

        if not region or not desc:
            messagebox.showerror("Error", "Please fill in Region and Description fields.")
            return

        add_outage(region, severity, status, desc)
        self.load_tree_data()
        self.reg_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def render_chart_view(self):
        self.current_view = 'chart'
        self.clear_main_area()

        ctk.CTkLabel(self.main_area, text="Grid Contingency & Outage Severity Analytics", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(0, 15))

        records = fetch_all_outages()
        severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for r in records:
            sev = r[2]
            if sev in severity_counts:
                severity_counts[sev] += 1

        # Theme-aware matplotlib styling
        current_mode = ctk.get_appearance_mode()
        bg_color = "#2b2b2b" if current_mode == "Dark" else "#f0f2f5"
        text_color = "white" if current_mode == "Dark" else "black"

        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        ax.bar(list(severity_counts.keys()), list(severity_counts.values()), color=['#2bc016', '#e6c817', '#e67e17', '#e61717'])

        ax.tick_params(colors=text_color, labelsize=10)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title("Outages by Severity Level", color=text_color, fontsize=12)

        canvas = FigureCanvasTkAgg(fig, master=self.main_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)


if __name__ == "__main__":
    app = GridCareApp()
    app.mainloop()