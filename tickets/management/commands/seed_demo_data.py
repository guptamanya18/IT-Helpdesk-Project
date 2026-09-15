import random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from tickets.models import Category, Ticket, Comment, TicketHistory


class Command(BaseCommand):
    help = "Seeds the database with demo users, categories and tickets so the app can be demoed immediately."

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # --- Admin -----------------------------------------------------
        admin, created = User.objects.get_or_create(
            username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        admin.profile.role = Profile.Role.ADMIN
        admin.profile.save()

        # --- Agents ------------------------------------------------------
        agents_data = [
            ('agent1', 'Priya', 'Sharma', 'Network'),
            ('agent2', 'Rohit', 'Verma', 'Hardware'),
            ('agent3', 'Ananya', 'Iyer', 'Software'),
        ]
        agents = []
        for username, first, last, dept in agents_data:
            user, created = User.objects.get_or_create(
                username=username, defaults={'email': f'{username}@example.com', 'first_name': first, 'last_name': last}
            )
            if created:
                user.set_password('agent12345')
                user.save()
            user.profile.role = Profile.Role.AGENT
            user.profile.department = dept
            user.profile.save()
            agents.append(user)

        # --- Employees ---------------------------------------------------
        employees_data = [
            ('employee1', 'Aman', 'Gupta', 'Sales'),
            ('employee2', 'Neha', 'Kapoor', 'Finance'),
            ('employee3', 'Karan', 'Singh', 'Marketing'),
        ]
        employees = []
        for username, first, last, dept in employees_data:
            user, created = User.objects.get_or_create(
                username=username, defaults={'email': f'{username}@example.com', 'first_name': first, 'last_name': last}
            )
            if created:
                user.set_password('employee12345')
                user.save()
            user.profile.role = Profile.Role.EMPLOYEE
            user.profile.department = dept
            user.profile.save()
            employees.append(user)

        # --- Categories ----------------------------------------------------
        category_names = [
            ('Network', 'VPN, Wi-Fi, internet connectivity issues'),
            ('Hardware', 'Laptops, monitors, printers, peripherals'),
            ('Software', 'Application installs, bugs, licensing'),
            ('Access / Permissions', 'Account access, password resets, permissions'),
            ('Other', 'Anything that does not fit the above'),
        ]
        categories = []
        for name, desc in category_names:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories.append(cat)

        # --- Sample tickets ------------------------------------------------
        sample_tickets = [
            ("VPN Connection Issue", "My laptop isn't connecting to the office VPN since this morning.", 'Network', 'HIGH', Ticket.Status.IN_PROGRESS),
            ("Printer not working on 3rd floor", "The HP printer on the 3rd floor shows an offline error.", 'Hardware', 'MEDIUM', Ticket.Status.OPEN),
            ("Need Photoshop license", "Requesting a Photoshop license for the design team.", 'Software', 'LOW', Ticket.Status.OPEN),
            ("Cannot access shared drive", "Getting 'Access Denied' on the Finance shared drive.", 'Access / Permissions', 'HIGH', Ticket.Status.ASSIGNED),
            ("Laptop battery draining fast", "Battery drops from 100% to 20% within an hour.", 'Hardware', 'MEDIUM', Ticket.Status.RESOLVED),
            ("Email sync issue on Outlook", "Outlook stopped syncing new emails since yesterday.", 'Software', 'CRITICAL', Ticket.Status.OPEN),
            ("Wi-Fi keeps disconnecting", "Wi-Fi drops every 10-15 minutes in the east wing.", 'Network', 'MEDIUM', Ticket.Status.CLOSED),
            ("Monitor flickering", "External monitor flickers randomly when connected via HDMI.", 'Hardware', 'LOW', Ticket.Status.OPEN),
        ]

        if Ticket.objects.count() == 0:
            for i, (title, desc, cat_name, priority, status) in enumerate(sample_tickets):
                category = next(c for c in categories if c.name == cat_name)
                creator = employees[i % len(employees)]
                ticket = Ticket.objects.create(
                    title=title, description=desc, category=category,
                    priority=priority, status=Ticket.Status.OPEN,
                    created_by=creator,
                )
                TicketHistory.objects.create(ticket=ticket, actor=creator, action=f"Ticket created with priority {priority}.")

                if status != Ticket.Status.OPEN:
                    agent = agents[i % len(agents)]
                    ticket.assigned_to = agent
                    ticket.status = status
                    if status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
                        ticket.resolution = "Issue investigated and fixed by the support team."
                        ticket.resolved_at = timezone.now()
                    if status == Ticket.Status.CLOSED:
                        ticket.closed_at = timezone.now()
                    ticket.save()
                    TicketHistory.objects.create(ticket=ticket, actor=agent, action=f"Assigned to {agent.username}, status set to {status}.")
                    Comment.objects.create(ticket=ticket, author=agent, body="Looking into this now, will update shortly.")

            self.stdout.write(self.style.SUCCESS(f"Created {len(sample_tickets)} sample tickets."))
        else:
            self.stdout.write("Tickets already exist, skipping ticket creation.")

        self.stdout.write(self.style.SUCCESS("Demo data ready!"))
        self.stdout.write("Login with: admin/admin123, agent1/agent12345, employee1/employee12345")
