# Integrated Systems Project

An integrated Data Science and Software Engineering platform featuring National Electricity Grid Network Analysis (using NetworkX, Folium, Streamlit), GridCare-Lite desktop outage management (using Tkinter, SQLite), and ClinicCare-Lite web-based administrative management (using Flask, REST).

## Overview

An end-to-end multi-application platform designed to simulate critical national infrastructure and administrative operations across three core modules:

### 1. National Electricity Grid Network Analysis

- Data preprocessing, multi-table joins, and topological graph modeling using NetworkX.
- Topological metrics (Centrality, PageRank, Bridges) and simplified $N-1$ contingency testing.
- Interactive GIS plotting (Folium/Plotly) and unified reporting dashboard (Streamlit).

### 2. GridCare-Lite (Utility Operations)

- Desktop application (Tkinter/PyQt) backed by SQLite/MySQL.
- Role-Based Access Control (Admin, Engineer, Technician, Customer Service).
- Automated fault-to-resolution tracking and work-order management.

### 3. ClinicCare-Lite (Administrative Healthcare Management)

- Web application (Flask/Bootstrap) for patient registration and non-diagnostic task routing.
- Secure authentication (bcrypt, regex validation) and file upload verification.
- Internal messaging, notification dispatch, and operational analytics.

## 📁 Project Directory Structure

```text
Integrated-Systems-Project/
├── .gitignore               # Excludes .venv, __pycache__, and .sqlite3/.db files from Git
├── README.md                # Project overview, directory structure, and setup guide
├── requirements.txt         # Shared Python dependencies (Pandas, NetworkX, Flask, etc.)
├── generate_data.py         # Synthetic dataset generator script (Seed 42)
├── data/
│   ├── raw/                 # Baseline CSVs (utilities.csv, substations.csv, lines.csv)
│   └── processed/           # Merged & cleaned data outputs for analysis
├── grid_analysis/          # NetworkX graph analysis & Folium GIS mapping scripts
├── gridcare_lite/           # Tkinter desktop outage management app & SQLite database backend
│   ├── app.py               # Desktop GUI application entry point
│   ├── database.py          # Database schema initialization & default user seed script
│   └── gridcare.db          # Local SQLite database file (ignored by Git)
├── cliniccare_lite/         # Flask web application for healthcare management
├── dashboard/               # Streamlit unified interactive management UI
├── docs/                    # ERDs, system architecture diagrams, and user manuals
│   └── GRIDCARE_ERD.md      # GridCare-Lite database schema documentation
└── tests/                   # Unit and integration test suites

```

---

## Getting Started

### Prerequisites

* Python 3.10 or higher
* Git

### Local Environment Setup

1. **Clone the repository:**

```bash
git clone [https://github.com/Josephgavor100/Integrated-Systems-Project.git](https://github.com/Josephgavor100/Integrated-Systems-Project.git)
cd Integrated-Systems-Project

```

2. **Switch to the integration branch:**

```bash
git checkout develop

```

3. **Set up & activate a virtual environment:**

* **Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```

* **macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate

```

4. **Install required dependencies:**

```bash
pip install -r requirements.txt

```

5. **Initialize the GridCare-Lite Database:**

```bash
python gridcare_lite/database.py

```

---

## ⚙️ Branching Rules & Contribution Workflow

To keep the repository clean and avoid code conflicts:

* Never commit directly to `main` or `develop`.

* Always create a feature branch off `develop` before working on a task:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<your-task-name>

```

* Push your feature branch and open a Pull Request (PR) into `develop` for review.
