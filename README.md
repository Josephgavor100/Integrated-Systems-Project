# Integrated-Systems-Project
A unified Data Science and Software Engineering platform featuring National Electricity Grid Network Analysis (NetworkX, Folium, Streamlit), GridCare-Lite desktop outage management (Tkinter, SQLite), and ClinicCare-Lite web-based administrative management (Flask, REST).

---
# CS 112 Summer 2026 Integrated Data Science & Software Engineering System

## Overview
An end-to-end multi-application platform designed to simulate critical national infrastructure and administrative operations across three core modules:

##### 1. National Electricity Grid Network Analysis:
   - Data preprocessing, multi-table joins, and topological graph modeling using *NetworkX*.
   - Topological metrics (Centrality, PageRank, Bridges) and simplified $N-1$ contingency testing.
   - Interactive GIS plotting (*Folium/Plotly*) and unified reporting dashboard (*Streamlit*).

##### 2. GridCare-Lite (Utility Operations):
   - Desktop application (*Tkinter/PyQt*) backed by SQLite/MySQL.
   - Role-Based Access Control (Admin, Engineer, Technician, Customer Service).
   - Automated fault-to-resolution tracking and work-order management.

##### 3. ClinicCare-Lite (Administrative Healthcare Management):
   - Web application (*Flask/Bootstrap*) for patient registration and non-diagnostic task routing.
   - Secure authentication (*bcrypt, regex validation*) and file upload verification.
   - Internal messaging, notification dispatch, and operational analytics.

