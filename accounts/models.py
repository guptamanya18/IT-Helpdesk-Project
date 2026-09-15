from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Extends Django's built-in User model with a 'role' so we can tell
    Employees, Support Agents and Admins apart without writing a whole
    custom auth system.
    """

    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        AGENT = 'AGENT', 'Support Agent'
        ADMIN = 'ADMIN', 'Admin'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active_agent = models.BooleanField(
        default=True,
        help_text="Uncheck to stop assigning new tickets to this agent (e.g. on leave)."
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile whenever a new User is created,
    so every user always has a role and we never hit a 'profile does
    not exist' error in views/templates.
    """
    if created:
        # Django superusers created via createsuperuser get ADMIN role automatically.
        role = Profile.Role.ADMIN if instance.is_superuser else Profile.Role.EMPLOYEE
        Profile.objects.create(user=instance, role=role)
    else:
        # Keep it safe even if a User existed before Profile did.
        Profile.objects.get_or_create(user=instance)
