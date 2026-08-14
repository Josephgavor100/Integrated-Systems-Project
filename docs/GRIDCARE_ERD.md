# GridCare-Lite Entity-Relationship Documentation

## 1. Overview

GridCare-Lite uses a relational SQLite database structure designed to support Role-Based Access Control (RBAC), asset tracking, fault management, and maintenance workflows. The schema consists of four primary entities: `users`, `substations`, `outages`, and `work_orders`.

---

## 2. Table Specifications

### `users`

Stores system users across administrative, engineering, field technician, and customer service roles.

* **`user_id`** (`INTEGER`, PK, AUTOINCREMENT): Unique identifier for each user.
  
* **`username`** (`TEXT`, UNIQUE, NOT NULL): System login name.
* **`password_hash`** (`TEXT`, NOT NULL): Hashed password string.
* **`role`** (`TEXT`, CHECK constraint): User authorization level (`'Admin'`, `'Engineer'`, `'Technician'`, `'Customer Service'`).
* **`full_name`** (`TEXT`, NOT NULL): User's full name.

### `substations`

Maintains reference data for physical power distribution assets.

* **`substation_id`** (`INTEGER`, PK): Unique grid substation identifier matching baseline data.
  
* **`name`** (`TEXT`, NOT NULL): Substation facility name.
* **`region`** (`TEXT`, NOT NULL): Administrative region.
* **`voltage_kv`** (`REAL`): Operating voltage level in kilovolts.
* **`capacity_mva`** (`REAL`): Transformer capacity rating in MVA.
* **`status`** (`TEXT`): Current operational state (`Active`, `Inactive`, `Under Maintenance`).

### `outages`

Logs reported system faults and power supply disruptions.

* **`outage_id`** (`INTEGER`, PK, AUTOINCREMENT): Unique incident identifier.
  
* **`substation_id`** (`INTEGER`, FK): Reference to the affected substation (`substations.substation_id`).
* **`reported_by`** (`INTEGER`, FK): Reference to the logging user (`users.user_id`).
* **`fault_type`** (`TEXT`, NOT NULL): Nature of failure (e.g., Transformer Overload, Line Trip).
* **`severity`** (`TEXT`, CHECK constraint): Fault priority level (`'Low'`, `'Medium'`, `'High'`, `'Critical'`).
* **`status`** (`TEXT`, CHECK constraint): Incident state (`'Open'`, `'Assigned'`, `'In Progress'`, `'Resolved'`).
* **`created_at`** (`TIMESTAMP`): Incident logging timestamp.

### `work_orders`

Tracks maintenance dispatch, technician assignment, and repair execution.

* **`work_order_id`** (`INTEGER`, PK, AUTOINCREMENT): Unique maintenance dispatch record.
  
* **`outage_id`** (`INTEGER`, FK, UNIQUE): Associated fault report (`outages.outage_id`).
* **`assigned_technician_id`** (`INTEGER`, FK): Field technician assigned (`users.user_id`).
* **`scheduled_date`** (`TEXT`): Target repair execution date.
* **`resolution_notes`** (`TEXT`): Field repair notes recorded upon completion.
* **`completed_at`** (`TIMESTAMP`): Time of issue resolution.

---

## 3. Entity Relationships & Cardinality

1. **Substation to Outage (1 : N)**
   * One substation can have multiple logged outages over time.
   * Every outage record must reference exactly one valid substation.

2. **User to Outage (1 : N)**
   * One user (Customer Service/Engineer) can log multiple outage reports.

3. **Outage to Work Order (1 : 1)**
   * An outage report generates at most **one** work order.
   * Every work order belongs to exactly **one** specific outage report.

4. **User to Work Order (1 : N)**
   * A field technician (`users.role = 'Technician'`) can be assigned to multiple work orders.
  