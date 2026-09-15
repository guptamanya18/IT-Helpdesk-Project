# IT Helpdesk — Ticket Management System

A full-featured internal IT support portal built with Django. Employees raise
tickets, support agents work through a queue, and administrators get an
organisation-wide analytics dashboard — all in a single, self-contained
application with no external services required.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Demo Credentials](#demo-credentials)
- [User Roles & Permissions](#user-roles--permissions)
- [Ticket Lifecycle](#ticket-lifecycle)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [URL Reference](#url-reference)
- [Client Demo Walkthrough](#client-demo-walkthrough)
- [Design System](#design-system)
- [Configuration](#configuration)
- [Production Checklist](#production-checklist)

---

## Features

### Employee portal
- Self-registration (sign up directly from the login page)
- Personal dashboard showing open, in-progress, and recently closed tickets
- Create tickets with title, description, category, and priority
- Comment thread on each ticket (two-way conversation with the assigned agent)
- Upload file attachments (screenshots, logs, documents)
- One-click confirmation to close a ticket once the agent marks it resolved

### Support agent portal
- Split queue view: tickets assigned to you vs. the unassigned pool
- "Pick up" a ticket from the unassigned queue in one click
- Update ticket status, priority, assigned agent, and resolution notes
- Full activity timeline showing every state change and who made it
- Key metrics: open tickets assigned, unassigned queue size, total resolved

### Admin portal
- Organisation-wide statistics: total, open, and closed ticket counts
- Breakdown tables: tickets by status, priority, and category
- Agent workload table showing open and total tickets per agent
- Create new support agent accounts directly from the admin panel
- Activate / deactivate individual agents (e.g. for leave or offboarding)
- Add and delete ticket categories
- Access to Django's built-in `/admin/` panel for raw data management

### Cross-cutting
- Role-based access control on every view (Employee / Agent / Admin)
- Complete audit trail — every status, priority, and assignment change is logged
- Searchable and filterable ticket list (by title/description, status, priority, category)
- Paginated results (10 tickets per page)
- Flash messages for all user actions (success / error / warning)
- Unique ticket numbers in `TCK-XXXX` format
- Responsive layout (Bootstrap 5 grid)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.x / 6.x |
| Database | SQLite (default, zero-config) |
| Image handling | Pillow |
| Frontend | Bootstrap 5.3, Bootstrap Icons 1.11 |
| Typography | Inter (Google Fonts) |
| Styling | Custom CSS design system (no SCSS, no build step) |
| Auth | Django built-in authentication |

No JavaScript framework, no message broker, no Docker — the entire stack runs
with a single `python manage.py runserver` command.

---

## Quick Start

### Prerequisites

- Python 3.10 or newer
- `pip`

### Setup

```bash
# 1. Clone or unzip the project
cd helpdesk_system

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database schema
python manage.py makemigrations
python manage.py migrate

# 5. Seed demo accounts and sample tickets
python manage.py seed_demo_data

# 6. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Demo Credentials

These accounts are created by the `seed_demo_data` management command.

| Role | Username | Password | Notes |
|---|---|---|---|
| Admin | `admin` | `admin123` | Full access; redirects to the statistics dashboard |
| Support Agent | `agent1` | `agent12345` | Assigned tickets + unassigned queue |
| Support Agent | `agent2` | `agent12345` | — |
| Support Agent | `agent3` | `agent12345` | — |
| Employee | `employee1` | `employee12345` | Can raise and manage their own tickets |
| Employee | `employee2` | `employee12345` | — |
| Employee | `employee3` | `employee12345` | — |

New employee accounts can also be self-registered from the login page by clicking
**Sign up**.

> **Note:** These credentials are for development and demonstration only.
> Never use them in a production environment.

---

## User Roles & Permissions

The application defines three roles, stored on the `Profile` model that extends
Django's built-in `User`.

### Employee
- Registers and logs in without admin involvement
- Can only see their own tickets — not those raised by other employees
- Can raise new tickets, post comments, and upload attachments
- Can close their own ticket once an agent marks it **Resolved**
- Cannot access agent or admin views

### Support Agent
- Created by an Admin (not self-registered)
- Sees all unassigned tickets and picks them up for assignment
- Can update ticket status, priority, assigned agent, and resolution notes
- Can force-close any ticket
- Cannot access the admin statistics or category/agent management pages

### Admin
- Has all agent capabilities
- Sees the organisation-wide statistics dashboard on login
- Can create and deactivate support agent accounts
- Can add and delete ticket categories
- Has access to Django's `/admin/` panel

Role assignment is automatic:
- A new self-registered user always gets the **Employee** role
- A Django superuser (`createsuperuser`) automatically gets the **Admin** role
- New agent accounts are created with the **Agent** role via the admin panel

---

## Ticket Lifecycle

Tickets move forward through a fixed five-stage pipeline. The current position
is shown as a progress bar on the ticket detail page.

```
OPEN  →  ASSIGNED  →  IN PROGRESS  →  RESOLVED  →  CLOSED
```

| Stage | Triggered by |
|---|---|
| **Open** | Employee creates the ticket |
| **Assigned** | Agent picks up the ticket (or is manually assigned) |
| **In Progress** | Agent sets status to In Progress |
| **Resolved** | Agent fills in resolution notes and marks resolved |
| **Closed** | Employee confirms the fix — or an agent/admin force-closes |

Assigning a still-**Open** ticket automatically advances it to **Assigned**.
`resolved_at` and `closed_at` timestamps are recorded automatically.

---

## Project Structure

```
helpdesk_system/
│
├── helpdesk/                  # Django project package
│   ├── settings.py            # All project settings
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                  # User profiles & authentication
│   ├── models.py              # Profile model (extends User with role)
│   ├── forms.py               # SignUpForm, AgentCreationForm
│   ├── views.py               # signup view
│   └── urls.py
│
├── tickets/                   # Core helpdesk logic
│   ├── models.py              # Category, Ticket, Comment, Attachment, TicketHistory
│   ├── forms.py               # TicketCreateForm, CommentForm, AgentUpdateForm, etc.
│   ├── views.py               # All ticket and admin views
│   ├── urls.py
│   ├── admin.py               # Django admin registrations
│   └── management/
│       └── commands/
│           └── seed_demo_data.py
│
├── templates/                 # Project-level templates
│   ├── base.html              # Site-wide layout (navbar, footer, flash messages)
│   └── registration/
│       ├── login.html
│       └── signup.html
│
├── tickets/templates/tickets/ # App-level templates
│   ├── employee_dashboard.html
│   ├── agent_dashboard.html
│   ├── admin_stats.html
│   ├── ticket_list.html
│   ├── ticket_detail.html
│   ├── ticket_form.html
│   ├── manage_agents.html
│   └── manage_categories.html
│
├── static/
│   └── css/
│       └── style.css          # Custom design system (Midnight Jade theme)
│
├── media/                     # User-uploaded file attachments (created at runtime)
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Data Models

### `accounts.Profile`

Extends Django's `User` via a `OneToOneField`. Created automatically via a
`post_save` signal whenever a new `User` is saved.

| Field | Type | Description |
|---|---|---|
| `user` | OneToOneField → User | The linked Django user |
| `role` | CharField | `EMPLOYEE`, `AGENT`, or `ADMIN` |
| `department` | CharField | Optional department name |
| `phone` | CharField | Optional phone number |
| `is_active_agent` | BooleanField | Inactive agents are excluded from assignment |

### `tickets.Category`

Simple lookup table for ticket categorisation.

| Field | Type | Description |
|---|---|---|
| `name` | CharField | Unique category name (e.g. Network, Hardware) |
| `description` | CharField | Optional short description |

### `tickets.Ticket`

The core entity. Priority and Status are defined as inner `TextChoices` classes.

| Field | Type | Description |
|---|---|---|
| `title` | CharField | Short summary of the issue |
| `description` | TextField | Full problem description |
| `category` | FK → Category | `SET_NULL` on category deletion |
| `priority` | CharField | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | CharField | `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| `created_by` | FK → User | The employee who raised the ticket |
| `assigned_to` | FK → User (nullable) | The agent currently handling it |
| `resolution` | TextField | Agent's resolution notes |
| `created_at` | DateTimeField | Auto-set on creation |
| `updated_at` | DateTimeField | Auto-updated on every save |
| `resolved_at` | DateTimeField | Set when status reaches `RESOLVED` |
| `closed_at` | DateTimeField | Set when status reaches `CLOSED` |

**Computed properties:** `ticket_number` (`TCK-XXXX`), `is_closed`,
`priority_badge_class`, `status_badge_class`, `status_progress_percent`.

### `tickets.Comment`

Threaded conversation on a ticket, ordered oldest-first.

| Field | Type | Description |
|---|---|---|
| `ticket` | FK → Ticket | |
| `author` | FK → User | Either the employee or the agent |
| `body` | TextField | Comment content |
| `created_at` | DateTimeField | |

### `tickets.Attachment`

Files uploaded to a ticket (screenshots, logs, etc.).

| Field | Type | Description |
|---|---|---|
| `ticket` | FK → Ticket | |
| `uploaded_by` | FK → User | |
| `file` | FileField | Stored under `media/attachments/YYYY/MM/` |
| `uploaded_at` | DateTimeField | |

### `tickets.TicketHistory`

Immutable audit log. One record is created for every meaningful change
(status, priority, assignment, attachment upload, close).

| Field | Type | Description |
|---|---|---|
| `ticket` | FK → Ticket | |
| `actor` | FK → User (nullable) | `SET_NULL` so history survives user deletion |
| `action` | CharField | Human-readable description of the change |
| `timestamp` | DateTimeField | Auto-set; ordered newest-first |

---

## URL Reference

| Method | URL | View | Access |
|---|---|---|---|
| GET/POST | `/accounts/login/` | Django `LoginView` | Public |
| POST | `/accounts/logout/` | Django `LogoutView` | Authenticated |
| GET/POST | `/accounts/signup/` | `accounts.views.signup` | Public |
| GET | `/` | `tickets.views.dashboard` | Authenticated (role-aware redirect) |
| GET | `/tickets/` | `tickets.views.ticket_list` | Authenticated |
| GET/POST | `/tickets/new/` | `tickets.views.ticket_create` | Employee |
| GET/POST | `/tickets/<id>/` | `tickets.views.ticket_detail` | Authenticated |
| GET | `/admin-panel/stats/` | `tickets.views.admin_stats` | Admin |
| GET/POST | `/admin-panel/agents/` | `tickets.views.manage_agents` | Admin |
| POST | `/admin-panel/agents/<id>/toggle/` | `tickets.views.toggle_agent_active` | Admin |
| GET/POST | `/admin-panel/categories/` | `tickets.views.manage_categories` | Admin |
| POST | `/admin-panel/categories/<id>/delete/` | `tickets.views.delete_category` | Admin |
| `*` | `/admin/` | Django admin site | Superuser |

---

## Client Demo Walkthrough

The following sequence demonstrates the complete ticket lifecycle end-to-end.
It is designed to be run live in front of a client or stakeholder.

### Step 1 — Employee raises a ticket

1. Log in as **`employee1`** (`employee12345`)
2. The employee dashboard shows stat cards and open tickets
3. Click **Raise Ticket** → fill in a title, description, category, and priority
4. Submit — you are redirected to the ticket detail page
5. The ticket number (`TCK-XXXX`), lifecycle progress bar (Open), and activity
   log are all visible immediately

### Step 2 — Agent works the queue

1. Log in as **`agent1`** (`agent12345`)
2. The support queue shows the new ticket in **Unassigned** — click **Pick up**
3. The ticket is now assigned to `agent1` and moves to **Assigned** automatically
4. Open the ticket → update status to **In Progress**
5. Post a comment to the employee (e.g. "Looking into this now")
6. Fill in resolution notes and set status to **Resolved**
7. Click **Update ticket** — `resolved_at` is recorded and the progress bar
   advances to the Resolved stage

### Step 3 — Employee confirms and closes

1. Log back in as **`employee1`**
2. The ticket now shows **Resolved** in the dashboard
3. Open it → click **Confirm fix & close ticket**
4. The ticket moves to **Closed** and disappears from the open list

### Step 4 — Admin reviews the dashboard

1. Log in as **`admin`** (`admin123`)
2. Redirected immediately to the **Statistics** dashboard
3. Show the four top-level stat cards (total, open, closed, agents)
4. Show the breakdown panels: tickets by status, priority, and category
5. Show the **Agent workload** table with open and total counts per agent
6. Navigate to **Agents** → demonstrate activating / deactivating an agent
7. Navigate to **Categories** → add a new category and show it appears on
   the ticket creation form

### Step 5 — Django admin panel

1. Still logged in as `admin`, visit **`/admin/`**
2. Show the raw data models: Tickets, Comments, Attachments, TicketHistory,
   Profiles, Categories
3. Useful for auditing, bulk operations, and explaining the data model

---

## Design System

The frontend uses a custom CSS design system built on top of Bootstrap 5.3,
with no build step required. All styles are in `static/css/style.css`.

**Colour palette — "Midnight Jade"**

| Token | Value | Usage |
|---|---|---|
| `--brand` | `#00c47a` | Primary accent (jade green) |
| `--brand-dark` | `#00a365` | Hover states, borders |
| `--nav-bg` | `#0a0f1e` | Navigation bar (obsidian dark) |
| `--surface` | `#ffffff` | Card backgrounds |
| `--bg` | `#f1f4f7` | Page background |
| `--text` | `#090e1a` | Headings |
| `--text-muted` | `#6b7891` | Secondary text, labels |

**Typography:** Inter (variable font, loaded from Google Fonts).
Font-feature settings `cv02 cv03 cv04 cv11` are enabled for the cleanest rendering.

**External CDN dependencies** (loaded in `base.html`, no local copies needed):

```
Bootstrap 5.3.3     cdn.jsdelivr.net/npm/bootstrap@5.3.3
Bootstrap Icons 1.11.3   cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3
Inter               fonts.googleapis.com
```

---

## Configuration

All configuration lives in `helpdesk/settings.py`.

| Setting | Default | Notes |
|---|---|---|
| `DEBUG` | `True` | **Must be `False` in production** |
| `DATABASES` | SQLite | Change to PostgreSQL for production |
| `TIME_ZONE` | `Asia/Kolkata` | Update to match your server timezone |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | Where uploaded attachments are stored |
| `LOGIN_REDIRECT_URL` | `'dashboard'` | Role-aware dashboard after login |
| `LOGOUT_REDIRECT_URL` | `'login'` | Redirect after logout |

---

## Production Checklist

Before deploying to a production server, complete the following:

- [ ] Set `DEBUG = False` in `settings.py`
- [ ] Replace `SECRET_KEY` with a long random value (use `secrets.token_hex(50)`)
- [ ] Add your domain to `ALLOWED_HOSTS`
- [ ] Switch `DATABASES` to PostgreSQL (or another production-grade engine)
- [ ] Configure a real email backend (replace `console.EmailBackend`)
- [ ] Run `python manage.py collectstatic` and serve `/static/` via Nginx or a CDN
- [ ] Serve `/media/` via Nginx or a cloud storage bucket (S3, GCS, etc.)
- [ ] Set `SECURE_SSL_REDIRECT = True` and configure HTTPS
- [ ] Create a production superuser with `python manage.py createsuperuser`
- [ ] Remove or restrict access to `/admin/` at the reverse-proxy level
- [ ] Set up regular database backups
