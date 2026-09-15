from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """e.g. Network, Hardware, Software, Access/Permissions, Other."""
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    # A ticket may only move forward along this path (used for validation
    # and for drawing the lifecycle progress bar in the template).
    STATUS_ORDER = [Status.OPEN, Status.ASSIGNED, Status.IN_PROGRESS, Status.RESOLVED, Status.CLOSED]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tickets')
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets'
    )

    resolution = models.TextField(blank=True, help_text="Filled in by the agent once resolved.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} {self.title}"

    def get_absolute_url(self):
        return reverse('ticket_detail', args=[self.id])

    # --- convenience helpers used by templates / views -----------------

    @property
    def ticket_number(self):
        return f"TCK-{self.id:04d}"

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def priority_badge_class(self):
        return {
            self.Priority.LOW: 'badge-low',
            self.Priority.MEDIUM: 'badge-medium',
            self.Priority.HIGH: 'badge-high',
            self.Priority.CRITICAL: 'badge-critical',
        }.get(self.priority, '')

    @property
    def status_badge_class(self):
        return {
            self.Status.OPEN: 'badge-open',
            self.Status.ASSIGNED: 'badge-assigned',
            self.Status.IN_PROGRESS: 'badge-progress',
            self.Status.RESOLVED: 'badge-resolved',
            self.Status.CLOSED: 'badge-closed',
        }.get(self.status, '')

    def status_progress_percent(self):
        """Used to render a lifecycle progress bar: OPEN..CLOSED -> 0..100."""
        try:
            idx = self.STATUS_ORDER.index(self.status)
        except ValueError:
            return 0
        return int(idx / (len(self.STATUS_ORDER) - 1) * 100)

    def mark_status(self, new_status, save=True):
        self.status = new_status
        if new_status == self.Status.RESOLVED and not self.resolved_at:
            self.resolved_at = timezone.now()
        if new_status == self.Status.CLOSED and not self.closed_at:
            self.closed_at = timezone.now()
        if save:
            self.save()


class Comment(models.Model):
    """A conversation thread on a ticket - employee <-> agent."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.ticket}"


class Attachment(models.Model):
    """Files (screenshots, logs) uploaded to a ticket."""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name.split('/')[-1]

    @property
    def filename(self):
        return self.file.name.split('/')[-1]


class TicketHistory(models.Model):
    """
    Audit trail: every time status/priority/assignment changes, we log it,
    so there's a visible timeline of what happened to a ticket and who did it.
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Ticket histories'

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.action}"
