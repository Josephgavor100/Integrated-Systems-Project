import csv
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
  sys.path.append(str(PROJECT_ROOT))

from grid_analysis.eda_analytics import GridEDAEngine
from grid_analysis.graph_analytics import GridNetworkAnalyzer
from gridcare_lite.database import (
    add_outage,
    create_user,
    fetch_all_outages,
    init_db,
    update_outage_status,
    verify_user,
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Role-Based Access Control Configuration ---
ROLE_PERMISSIONS = {
    "Admin": {
        "can_add_outage": True,
        "can_update_status": True,
        "can_view_analytics": True,
    },
    "Engineer": {
        "can_add_outage": True,
        "can_update_status": True,
        "can_view_analytics": True,
    },
    "Technician": {
        "can_add_outage": False,
        "can_update_status": True,
        "can_view_analytics": True,
    },
    "Customer Service": {
        "can_add_outage": False,
        "can_update_status": False,
        "can_view_analytics": False,
    },
}


def check_permission(user_role: str, action: str) -> bool:
  """Helper method to verify role capabilities."""
  role_cfg = ROLE_PERMISSIONS.get(user_role, {})
  return role_cfg.get(action, False)


class GridCareApp(ctk.CTk):

  def __init__(self):
    super().__init__()
    self.title("GridCare-Lite | National Grid Operational Dashboard")
    self.geometry("1050x680")
    self.minsize(950, 600)

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
    dashboard_frame = DashboardFrame(
        parent=self.container, controller=self, user=user_info
    )
    dashboard_frame.grid(row=0, column=0, sticky="nsew")
    dashboard_frame.tkraise()


class LoginFrame(ctk.CTkFrame):

  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller

    card = ctk.CTkFrame(self, corner_radius=15, width=400, height=520)
    card.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        card, text="⚡ GridCare-Lite", font=ctk.CTkFont(size=24, weight="bold")
    ).pack(pady=(20, 2))
    ctk.CTkLabel(
        card, text="National Grid Utility Portal", text_color="gray"
    ).pack(pady=(0, 10))

    self.tabview = ctk.CTkTabview(card, width=320, height=380)
    self.tabview.pack(pady=5, padx=20)

    self.tab_login = self.tabview.add("Sign In")
    self.tab_register = self.tabview.add("Create Account")

    # --- SIGN IN TAB ---
    self.username_entry = ctk.CTkEntry(
        self.tab_login, placeholder_text="Username", width=260, height=35
    )
    self.username_entry.pack(pady=8)

    self.password_entry = ctk.CTkEntry(
        self.tab_login,
        placeholder_text="Password",
        show="•",
        width=260,
        height=35,
    )
    self.password_entry.pack(pady=8)

    self.theme_menu = ctk.CTkOptionMenu(
        self.tab_login,
        values=["Dark", "Light", "System"],
        width=260,
        height=32,
        command=lambda mode: ctk.set_appearance_mode(mode),
    )
    self.theme_menu.set(ctk.get_appearance_mode())
    self.theme_menu.pack(pady=8)

    ctk.CTkButton(
        self.tab_login,
        text="Sign In",
        width=260,
        height=35,
        command=self.handle_login,
    ).pack(pady=12)
    self.status_label = ctk.CTkLabel(
        self.tab_login, text="", text_color="#ff5555"
    )
    self.status_label.pack(pady=2)

    # --- CREATE ACCOUNT TAB ---
    self.reg_fullname = ctk.CTkEntry(
        self.tab_register, placeholder_text="Full Name", width=260, height=35
    )
    self.reg_fullname.pack(pady=6)

    self.reg_username = ctk.CTkEntry(
        self.tab_register, placeholder_text="Username", width=260, height=35
    )
    self.reg_username.pack(pady=6)

    self.reg_password = ctk.CTkEntry(
        self.tab_register,
        placeholder_text="Password",
        show="•",
        width=260,
        height=35,
    )
    self.reg_password.pack(pady=6)

    self.reg_role = ctk.CTkOptionMenu(
        self.tab_register,
        values=["Engineer", "Technician", "Customer Service"],
        width=260,
        height=32,
    )
    self.reg_role.pack(pady=6)

    ctk.CTkButton(
        self.tab_register,
        text="Register Account",
        width=260,
        height=35,
        command=self.handle_register,
    ).pack(pady=10)
    self.reg_status_label = ctk.CTkLabel(
        self.tab_register, text="", text_color="#ff5555"
    )
    self.reg_status_label.pack(pady=2)

  def handle_login(self):
    username = self.username_entry.get().strip()
    password = self.password_entry.get().strip()

    user = verify_user(username, password)
    if user:
      self.status_label.configure(text="")
      self.controller.show_dashboard_view(user)
    else:
      self.status_label.configure(
          text="Invalid credentials (Try: admin / admin123)"
      )

  def handle_register(self):
    full_name = self.reg_fullname.get().strip()
    username = self.reg_username.get().strip()
    password = self.reg_password.get().strip()
    role = self.reg_role.get()

    if not full_name or not username or not password:
      self.reg_status_label.configure(
          text="Please fill in all fields", text_color="#ff5555"
      )
      return

    success, msg = create_user(username, password, role, full_name)
    if success:
      self.reg_status_label.configure(text=msg, text_color="#2bc016")
      self.reg_fullname.delete(0, tk.END)
      self.reg_username.delete(0, tk.END)
      self.reg_password.delete(0, tk.END)
    else:
      self.reg_status_label.configure(text=msg, text_color="#ff5555")


class DashboardFrame(ctk.CTkFrame):

  def __init__(self, parent, controller, user):
    super().__init__(parent)
    self.controller = controller
    self.user = user

    data_file = PROJECT_ROOT / "data" / "processed" / "processed_data.csv"
    self.analyzer = GridNetworkAnalyzer(data_path=str(data_file))
    self.analyzer.load_data_and_build_graph()

    self.eda_engine = GridEDAEngine(processed_data_path=str(data_file))
    self.eda_engine.load_data()

    # Sidebar setup
    sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(
        sidebar, text="⚡ GridCare", font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=(20, 10))
    ctk.CTkLabel(
        sidebar,
        text=f"User: {user['username']}\nRole: {user['role']}",
        text_color="gray",
        font=ctk.CTkFont(size=12),
    ).pack(pady=(0, 20))

    ctk.CTkButton(
        sidebar,
        text="Dashboard & Logs",
        width=160,
        command=self.render_logs_view,
    ).pack(pady=8)
    ctk.CTkButton(
        sidebar,
        text="Severity Analytics",
        width=160,
        command=self.render_chart_view,
    ).pack(pady=8)
    ctk.CTkButton(
        sidebar,
        text="Grid Topology (N-1)",
        width=160,
        command=self.render_network_view,
    ).pack(pady=8)
    ctk.CTkButton(
        sidebar,
        text="Asset Aging & Load",
        width=160,
        command=self.render_eda_view,
    ).pack(pady=8)

    self.theme_menu = ctk.CTkOptionMenu(
        sidebar,
        values=["Dark", "Light", "System"],
        width=160,
        command=self.change_appearance_mode,
    )
    self.theme_menu.set(ctk.get_appearance_mode())
    self.theme_menu.pack(side="bottom", pady=(0, 15))

    ctk.CTkButton(
        sidebar,
        text="Logout",
        fg_color="#d32f2f",
        hover_color="#9a0007",
        width=160,
        command=lambda: controller.show_login_view(),
    ).pack(side="bottom", pady=(0, 15))

    self.main_area = ctk.CTkFrame(self, fg_color="transparent")
    self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    self.render_logs_view()

  def change_appearance_mode(self, new_mode: str):
    ctk.set_appearance_mode(new_mode)
    self.update_treeview_theme(new_mode)
    if hasattr(self, "current_view"):
      if self.current_view == "chart":
        self.render_chart_view()
      elif self.current_view == "network":
        self.render_network_view()
      elif self.current_view == "eda":
        self.render_eda_view()

  def update_treeview_theme(self, mode: str):
    style = ttk.Style()
    style.theme_use("clam")
    if mode == "Light":
      style.configure(
          "Treeview",
          background="#ffffff",
          foreground="#000000",
          fieldbackground="#ffffff",
          rowheight=25,
      )
      style.map("Treeview", background=[("selected", "#3b8ed0")])
    else:
      style.configure(
          "Treeview",
          background="#2b2b2b",
          foreground="white",
          fieldbackground="#2b2b2b",
          rowheight=25,
      )
      style.map("Treeview", background=[("selected", "#1f538d")])

  def clear_main_area(self):
    """Clears main panel widgets and closes all open Matplotlib figures to prevent memory leaks."""
    plt.close("all")
    for widget in self.main_area.winfo_children():
      widget.destroy()

  def render_logs_view(self):
    self.current_view = "logs"
    self.clear_main_area()

    ctk.CTkLabel(
        self.main_area,
        text="Outage Management & Operations",
        font=ctk.CTkFont(size=22, weight="bold"),
    ).pack(anchor="w", pady=(0, 10))

    # --- SEARCH, FILTER & EXPORT BAR ---
    filter_bar = ctk.CTkFrame(self.main_area)
    filter_bar.pack(fill="x", pady=(0, 10), padx=5, ipady=3)

    self.search_entry = ctk.CTkEntry(
        filter_bar, placeholder_text="🔍 Search region or desc...", width=200
    )
    self.search_entry.pack(side="left", padx=5, pady=5)
    self.search_entry.bind("<KeyRelease>", lambda e: self.load_tree_data())

    self.filter_status_option = ctk.CTkOptionMenu(
        filter_bar,
        values=["All Statuses", "Active", "Investigating", "Resolved"],
        width=130,
        command=lambda _: self.load_tree_data(),
    )
    self.filter_status_option.pack(side="left", padx=5, pady=5)

    ctk.CTkButton(
        filter_bar,
        text="Reset",
        width=70,
        fg_color="#555555",
        command=self.reset_filters,
    ).pack(side="left", padx=5, pady=5)

    ctk.CTkButton(
        filter_bar,
        text="📁 Export Data",
        width=110,
        fg_color="#2bc016",
        hover_color="#1f8a10",
        command=self.export_data_dialog,
    ).pack(side="right", padx=5, pady=5)

    # Form for logging outages
    if check_permission(self.user["role"], "can_add_outage"):
      form_frame = ctk.CTkFrame(self.main_area)
      form_frame.pack(fill="x", pady=(0, 10), padx=5, ipady=5)

      self.reg_entry = ctk.CTkEntry(
          form_frame, placeholder_text="Region", width=140
      )
      self.reg_entry.grid(row=0, column=0, padx=5, pady=5)

      self.sev_option = ctk.CTkOptionMenu(
          form_frame,
          values=["Low", "Medium", "High", "Critical"],
          width=130,
      )
      self.sev_option.grid(row=0, column=1, padx=5, pady=5)

      self.stat_option = ctk.CTkOptionMenu(
          form_frame,
          values=["Active", "Investigating", "Resolved"],
          width=130,
      )
      self.stat_option.grid(row=0, column=2, padx=5, pady=5)

      self.desc_entry = ctk.CTkEntry(
          form_frame, placeholder_text="Description", width=220
      )
      self.desc_entry.grid(row=0, column=3, padx=5, pady=5)

      ctk.CTkButton(
          form_frame,
          text="Log Outage",
          width=110,
          command=self.handle_add_outage,
      ).grid(row=0, column=4, padx=5, pady=5)

    table_frame = ctk.CTkFrame(self.main_area)
    table_frame.pack(fill="both", expand=True, padx=5, pady=5)

    cols = ("ID", "Region", "Severity", "Status", "Description", "Timestamp")
    self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
    self.update_treeview_theme(ctk.get_appearance_mode())

    for col in cols:
      self.tree.heading(col, text=col)
      self.tree.column(
          col, anchor="center", width=110 if col != "Description" else 200
      )

    self.tree.pack(fill="both", expand=True)
    self.load_tree_data()

    if check_permission(self.user["role"], "can_update_status"):
      action_frame = ctk.CTkFrame(self.main_area)
      action_frame.pack(fill="x", pady=10)

      ctk.CTkLabel(
          action_frame, text="Update Status for Selected Outage:"
      ).pack(side="left", padx=10)
      self.update_status_option = ctk.CTkOptionMenu(
          action_frame,
          values=["Active", "Investigating", "Resolved"],
          width=140,
      )
      self.update_status_option.pack(side="left", padx=5)
      ctk.CTkButton(
          action_frame,
          text="Apply Status Update",
          command=self.handle_update_status,
      ).pack(side="left", padx=10)

  def load_tree_data(self):
    """Populates Treeview based on active search terms and status filters."""
    for item in self.tree.get_children():
      self.tree.delete(item)

    search_query = getattr(self, "search_entry", None)
    query = search_query.get().strip().lower() if search_query else ""

    status_filter = getattr(self, "filter_status_option", None)
    selected_status = status_filter.get() if status_filter else "All Statuses"

    rows = fetch_all_outages()
    for row in rows:
      outage_id, region, severity, status, desc, timestamp = row

      # Apply Status Filter
      if selected_status != "All Statuses" and status != selected_status:
        continue

      # Apply Text Search Filter
      if query:
        in_region = query in str(region).lower()
        in_desc = query in str(desc).lower()
        if not (in_region or in_desc):
          continue

      self.tree.insert("", "end", values=row)

  def reset_filters(self):
    if hasattr(self, "search_entry"):
      self.search_entry.delete(0, tk.END)
    if hasattr(self, "filter_status_option"):
      self.filter_status_option.set("All Statuses")
    self.load_tree_data()

  def export_data_dialog(self):
    """Export visible treeview rows to CSV or Excel."""
    visible_items = [
        self.tree.item(item)["values"] for item in self.tree.get_children()
    ]

    if not visible_items:
      messagebox.showwarning(
          "Export Warning", "No records available in current view to export."
      )
      return

    cols = ["ID", "Region", "Severity", "Status", "Description", "Timestamp"]

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV File", "*.csv"), ("Excel Spreadsheet", "*.xlsx")],
        title="Export Outage Data",
    )
    if not file_path:
      return

    try:
      if file_path.endswith(".xlsx"):
        df = pd.DataFrame(visible_items, columns=cols)
        df.to_excel(file_path, index=False)
      else:
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
          writer = csv.writer(f)
          writer.writerow(cols)
          writer.writerows(visible_items)

      messagebox.showinfo(
          "Export Successful", f"Data exported successfully to:\n{file_path}"
      )
    except Exception as e:
      messagebox.showerror("Export Error", f"Failed to export data: {e}")

  def handle_add_outage(self):
    region = self.reg_entry.get().strip()
    severity = self.sev_option.get()
    status = self.stat_option.get()
    desc = self.desc_entry.get().strip()

    if not region or not desc:
      messagebox.showerror(
          "Validation Error",
          "Please fill in all required fields (Region & Description).",
      )
      return

    add_outage(region, severity, status, desc)
    self.load_tree_data()
    self.reg_entry.delete(0, tk.END)
    self.desc_entry.delete(0, tk.END)
    messagebox.showinfo("Success", "Outage record successfully logged.")

  def handle_update_status(self):
    selected_item = self.tree.selection()
    if not selected_item:
      messagebox.showwarning(
          "Selection Required",
          "Please select an outage row from the grid table first.",
      )
      return

    outage_id = self.tree.item(selected_item[0])["values"][0]
    new_status = self.update_status_option.get()

    update_outage_status(outage_id, new_status)
    self.load_tree_data()
    messagebox.showinfo(
        "Status Updated", f"Outage ID {outage_id} status changed to '{new_status}'."
    )

  def render_chart_view(self):
    self.current_view = "chart"
    self.clear_main_area()

    ctk.CTkLabel(
        self.main_area,
        text="Grid Outage Severity Analytics",
        font=ctk.CTkFont(size=22, weight="bold"),
    ).pack(anchor="w", pady=(0, 15))

    records = fetch_all_outages()
    severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for r in records:
      sev = r[2]
      if sev in severity_counts:
        severity_counts[sev] += 1

    current_mode = ctk.get_appearance_mode()
    bg_color = "#2b2b2b" if current_mode == "Dark" else "#f0f2f5"
    text_color = "white" if current_mode == "Dark" else "black"

    fig, ax = plt.subplots(figsize=(6, 3.5), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    ax.bar(
        list(severity_counts.keys()),
        list(severity_counts.values()),
        color=["#2bc016", "#e6c817", "#e67e17", "#e61717"],
    )

    ax.tick_params(colors=text_color, labelsize=10)
    ax.spines["bottom"].set_color(text_color)
    ax.spines["left"].set_color(text_color)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", linestyle="--", alpha=0.2, color=text_color)
    ax.set_title("Outages by Severity Level", color=text_color, fontsize=12)

    canvas = FigureCanvasTkAgg(fig, master=self.main_area)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

  def render_network_view(self):
    self.current_view = "network"
    self.clear_main_area()

    ctk.CTkLabel(
        self.main_area,
        text="National Power Grid Network Topology & N-1 Contingency",
        font=ctk.CTkFont(size=22, weight="bold"),
    ).pack(anchor="w", pady=(0, 10))

    content_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
    content_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(content_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

    right_frame = ctk.CTkFrame(content_frame, width=350)
    right_frame.pack(side="right", fill="both", expand=False, padx=(5, 0))

    fig = self.analyzer.render_network_figure()
    current_mode = ctk.get_appearance_mode()
    bg_color = "#2b2b2b" if current_mode == "Dark" else "#ffffff"
    fig.patch.set_facecolor(bg_color)

    canvas = FigureCanvasTkAgg(fig, master=left_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

    contingency_data = self.analyzer.run_n1_contingency()
    critical_lines = contingency_data.get("critical_n1_lines", [])

    alert_box = ctk.CTkFrame(
        left_frame,
        fg_color="#3a2323" if current_mode == "Dark" else "#ffebee",
        corner_radius=8,
    )
    alert_box.pack(fill="x", padx=10, pady=10)

    alert_title = f"⚠️ N-1 Contingency Alert: {len(critical_lines)} Critical Vulnerability Line(s) Found"
    ctk.CTkLabel(
        alert_box,
        text=alert_title,
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#ff5555",
    ).pack(anchor="w", padx=10, pady=(5, 2))

    critical_desc = ", ".join([
        f"Line {c['line_id']} ({c['source']}->{c['target']})"
        for c in critical_lines[:3]
    ])
    if len(critical_lines) > 3:
      critical_desc += f" and {len(critical_lines) - 3} more..."

    ctk.CTkLabel(
        alert_box,
        text=(
            "Single points of failure:"
            f" {critical_desc if critical_lines else 'None (Grid is robust)'}"
        ),
        font=ctk.CTkFont(size=11),
    ).pack(anchor="w", padx=10, pady=(0, 5))

    ctk.CTkLabel(
        right_frame,
        text="Substation Centrality Metrics",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).pack(pady=10)

    metrics_df = self.analyzer.calculate_centrality_metrics()

    cols = ("Node ID", "Name", "Degree", "Betweenness")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=15)
    self.update_treeview_theme(current_mode)

    tree.heading("Node ID", text="ID")
    tree.column("Node ID", width=60, anchor="center")
    tree.heading("Name", text="Substation")
    tree.column("Name", width=120, anchor="w")
    tree.heading("Degree", text="Deg")
    tree.column("Degree", width=50, anchor="center")
    tree.heading("Betweenness", text="Betweenness")
    tree.column("Betweenness", width=90, anchor="center")

    for _, row in metrics_df.iterrows():
      tree.insert(
          "",
          "end",
          values=(
              row["substation_id"],
              row["name"],
              row["degree"],
              row["betweenness_centrality"],
          ),
      )

    tree.pack(fill="both", expand=True, padx=5, pady=5)

  def render_eda_view(self):
    """Render Operational Analytics & Asset Aging Metrics with detailed charts."""
    self.current_view = "eda"
    self.clear_main_area()

    ctk.CTkLabel(
        self.main_area,
        text="Substation Infrastructure & Asset Analytics",
        font=ctk.CTkFont(size=22, weight="bold"),
    ).pack(anchor="w", pady=(0, 15))

    # 1. KPI Metric Cards Top Bar
    summary = self.eda_engine.get_capacity_summary()
    cards_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
    cards_frame.pack(fill="x", pady=(0, 15))

    self._create_kpi_card(
        cards_frame, "Avg Utilization", f"{summary.get('avg_utilization', 0)}%", 0
    )
    self._create_kpi_card(
        cards_frame,
        "Overloaded Nodes (>90%)",
        str(summary.get("overloaded_count", 0)),
        1,
    )
    self._create_kpi_card(
        cards_frame,
        "Avg Asset Age",
        f"{summary.get('avg_asset_age', 0)} yrs",
        2,
    )
    self._create_kpi_card(
        cards_frame,
        "Aging Assets (>30 yrs)",
        str(summary.get("critical_age_count", 0)),
        3,
    )

    # 2. Charts Visualization Frame
    charts_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
    charts_frame.pack(fill="both", expand=True)

    df = self.eda_engine.df
    if df is None or df.empty:
      ctk.CTkLabel(
          charts_frame, text="No EDA dataset loaded.", text_color="#ff5555"
      ).pack(pady=20)
      return

    current_mode = ctk.get_appearance_mode()
    bg_color = "#2b2b2b" if current_mode == "Dark" else "#f0f2f5"
    text_color = "white" if current_mode == "Dark" else "black"

    try:
      fig, (ax1, ax2) = plt.subplots(
          1, 2, figsize=(9.5, 4.0), facecolor=bg_color
      )
      fig.subplots_adjust(
          bottom=0.18, top=0.80, wspace=0.3, left=0.08, right=0.96
      )

      age_col = "age_years" if "age_years" in df.columns else df.columns[0]

      util_col = "utilization_pct"
      if util_col not in df.columns:
        for alt in ["utilization_rate", "utilization", "load_pct"]:
          if alt in df.columns:
            util_col = alt
            break
        else:
          util_col = df.columns[1] if len(df.columns) > 1 else age_col

      # Plot 1: Asset Age Histogram
      ax1.set_facecolor(bg_color)
      ax1.hist(
          df[age_col].dropna(), bins=10, color="#3b8ed0", edgecolor=bg_color
      )
      ax1.set_title(
          "Substation Age Distribution",
          color=text_color,
          fontsize=11,
          fontweight="bold",
          pad=12,
      )
      ax1.set_xlabel("Age (Years)", color=text_color)
      ax1.set_ylabel("Count", color=text_color)
      ax1.tick_params(colors=text_color)
      ax1.spines["bottom"].set_color(text_color)
      ax1.spines["left"].set_color(text_color)
      ax1.spines["top"].set_visible(False)
      ax1.spines["right"].set_visible(False)
      ax1.grid(True, axis="y", linestyle="--", alpha=0.15, color=text_color)

      # Plot 2: Capacity Utilization Scatter Plot
      ax2.set_facecolor(bg_color)
      ax2.scatter(
          df[age_col],
          df[util_col],
          color="#e67e17",
          alpha=0.75,
          edgecolors="none",
      )
      ax2.axhline(
          90,
          color="#ff5555",
          linestyle="--",
          linewidth=1.2,
          label="Overload Limit (90%)",
      )
      ax2.set_title(
          "Utilization vs. Asset Age",
          color=text_color,
          fontsize=11,
          fontweight="bold",
          pad=12,
      )
      ax2.set_xlabel("Age (Years)", color=text_color)
      ax2.set_ylabel("Utilization (%)", color=text_color)

      ax2.legend(
          loc="upper left",
          facecolor=bg_color,
          edgecolor=text_color,
          labelcolor=text_color,
          fontsize=8,
      )
      ax2.tick_params(colors=text_color)
      ax2.spines["bottom"].set_color(text_color)
      ax2.spines["left"].set_color(text_color)
      ax2.spines["top"].set_visible(False)
      ax2.spines["right"].set_visible(False)
      ax2.grid(True, linestyle="--", alpha=0.15, color=text_color)

      canvas = FigureCanvasTkAgg(fig, master=charts_frame)
      canvas.draw()
      canvas_widget = canvas.get_tk_widget()
      canvas_widget.pack(fill="both", expand=True)

    except Exception as e:
      ctk.CTkLabel(
          charts_frame, text=f"Error rendering charts: {e}", text_color="#ff5555"
      ).pack(pady=20)

  def _create_kpi_card(self, parent, title, value, col):
    card = ctk.CTkFrame(parent, corner_radius=10)
    card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
    parent.grid_columnconfigure(col, weight=1)

    ctk.CTkLabel(
        card, text=title, font=ctk.CTkFont(size=12), text_color="gray"
    ).pack(pady=(10, 2), padx=10)
    ctk.CTkLabel(
        card, text=value, font=ctk.CTkFont(size=20, weight="bold")
    ).pack(pady=(0, 10), padx=10)


if __name__ == "__main__":
  app = GridCareApp()
  app.mainloop()