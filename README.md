# 🎫 IT Helpdesk / Ticket Management System

A Django-based support ticketing system with three roles (Employee, Support
Agent, Admin), a full ticket lifecycle, comments, file attachments, and an
admin statistics dashboard.

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database tables
python manage.py makemigrations
python manage.py migrate

# 4. Load demo data (admin, agents, employees, sample tickets)
python manage.py seed_demo_data

# 5. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

## Demo logins (created by `seed_demo_data`)

| Role     | Username  | Password       |
|----------|-----------|----------------|
| Admin    | admin     | admin123       |
| Agent    | agent1    | agent12345     |
| Agent    | agent2    | agent12345     |
| Agent    | agent3    | agent12345     |
| Employee | employee1 | employee12345  |
| Employee | employee2 | employee12345  |
| Employee | employee3 | employee12345  |

You can also sign up new Employee accounts from the Login page ("Sign up").

## What to demo to a client

1. Log in as **employee1** → raise a new ticket → see it on the dashboard.
2. Log in as **agent1** → pick it up from the unassigned queue → change
   status/priority → write a resolution.
3. Log in back as **employee1** → confirm and close the ticket.
4. Log in as **admin** → show the statistics dashboard, agent workload,
   and category management.
5. Open `/admin/` (Django's built-in admin) to show the raw data model.

See `PROJECT_EXPLANATION.md` for the full technical write-up.
