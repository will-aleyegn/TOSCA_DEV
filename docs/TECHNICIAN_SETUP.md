# Technician Setup for Subject Widget

The subject widget now includes a dropdown with the following technicians:
- Admin
- Will
- Operator 1
- Operator 2

## Adding Technicians to Database

These technicians must be added to the database before use. You can add them via:

### Option 1: Python Script

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("data/tosca.db")
db.initialize()

# Add technicians
db.create_technician(username="admin", full_name="Administrator", role="admin")
db.create_technician(username="will", full_name="Will Aleyegn", role="operator")
db.create_technician(username="operator1", full_name="Operator 1", role="operator")
db.create_technician(username="operator2", full_name="Operator 2", role="operator")
```

### Option 2: SQL Direct

```sql
INSERT INTO technicians (username, full_name, role, created_date) VALUES
  ('admin', 'Administrator', 'admin', datetime('now')),
  ('will', 'Will Aleyegn', 'operator', datetime('now')),
  ('operator1', 'Operator 1', 'operator', datetime('now')),
  ('operator2', 'Operator 2', 'operator', datetime('now'));
```

### Option 3: Check Existing

```bash
# Check if technicians already exist
sqlite3 data/tosca.db "SELECT username, full_name, role FROM technicians;"
```

## Notes

- The "admin" technician should already exist from database initialization
- Add "will", "operator1", "operator2" before first use
- Technician usernames are case-sensitive
- Full names can be updated as needed
