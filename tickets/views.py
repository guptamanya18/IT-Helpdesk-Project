from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TicketCreateForm, CommentForm, AttachmentForm, AgentUpdateForm, CategoryForm
from .models import Ticket, Category, Comment, Attachment, TicketHistory


# ---------------------------------------------------------------------------
# Small role-check helpers (kept simple/explicit rather than a permissions
# framework, since this is a teaching project)
# ---------------------------------------------------------------------------

def _is_agent(user):
    return hasattr(user, 'profile') and user.profile.is_agent

def _is_admin(user):
    return hasattr(user, 'profile') and user.profile.is_admin_role

def _is_staff_role(user):
    return _is_agent(user) or _is_admin(user)


@login_required
def dashboard(request):
    """
    Landing page after login. Content differs by role:
    - Employee: their own tickets + quick-create
    - Agent: tickets assigned to them + unassigned queue
    - Admin: org-wide stats
    """
    profile = request.user.profile

    if profile.is_admin_role:
        return redirect('admin_stats')

    if profile.is_agent:
        assigned = Ticket.objects.filter(assigned_to=request.user).exclude(status=Ticket.Status.CLOSED)
        unassigned = Ticket.objects.filter(assigned_to__isnull=True).exclude(status=Ticket.Status.CLOSED)
        context = {
            'assigned_tickets': assigned,
            'unassigned_tickets': unassigned,
            'resolved_count': Ticket.objects.filter(assigned_to=request.user, status=Ticket.Status.RESOLVED).count(),
        }
        return render(request, 'tickets/agent_dashboard.html', context)

    # Employee
    my_tickets = Ticket.objects.filter(created_by=request.user)
    context = {
        'open_tickets': my_tickets.exclude(status=Ticket.Status.CLOSED),
        'closed_tickets': my_tickets.filter(status=Ticket.Status.CLOSED),
        'total': my_tickets.count(),
    }
    return render(request, 'tickets/employee_dashboard.html', context)


@login_required
def ticket_list(request):
    """Full searchable/filterable list. Employees see only their own; agents/admins see all."""
    profile = request.user.profile
    tickets = Ticket.objects.select_related('category', 'assigned_to', 'created_by')

    if profile.is_employee:
        tickets = tickets.filter(created_by=request.user)

    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    q = request.GET.get('q')

    if status:
        tickets = tickets.filter(status=status)
    if priority:
        tickets = tickets.filter(priority=priority)
    if category:
        tickets = tickets.filter(category_id=category)
    if q:
        tickets = tickets.filter(Q(title__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(tickets, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'status_choices': Ticket.Status.choices,
        'priority_choices': Ticket.Priority.choices,
        'current_status': status or '',
        'current_priority': priority or '',
        'current_category': category or '',
        'query': q or '',
    }
    return render(request, 'tickets/ticket_list.html', context)


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            TicketHistory.objects.create(
                ticket=ticket, actor=request.user,
                action=f"Ticket created with priority {ticket.get_priority_display()}."
            )
            messages.success(request, f"Ticket {ticket.ticket_number} created successfully.")
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket.objects.select_related('category', 'created_by', 'assigned_to'), pk=pk)
    profile = request.user.profile

    # Access control: employees may only view their own tickets.
    if profile.is_employee and ticket.created_by_id != request.user.id:
        return HttpResponseForbidden("You do not have permission to view this ticket.")

    comment_form = CommentForm()
    attachment_form = AttachmentForm()
    agent_form = AgentUpdateForm(instance=ticket) if _is_staff_role(request.user) else None

    if request.method == 'POST':
        # Distinguish which form was submitted via a hidden 'form_name' field.
        form_name = request.POST.get('form_name')

        if form_name == 'comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added.")
                return redirect('ticket_detail', pk=pk)

        elif form_name == 'attachment':
            attachment_form = AttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.save()
                TicketHistory.objects.create(
                    ticket=ticket, actor=request.user,
                    action=f"Attachment uploaded: {attachment.filename}"
                )
                messages.success(request, "Attachment uploaded.")
                return redirect('ticket_detail', pk=pk)

        elif form_name == 'agent_update' and _is_staff_role(request.user):
            old_status, old_priority, old_assignee = ticket.status, ticket.priority, ticket.assigned_to
            agent_form = AgentUpdateForm(request.POST, instance=ticket)
            if agent_form.is_valid():
                updated_ticket = agent_form.save(commit=False)

                # Auto-progress: assigning a still-OPEN ticket bumps it to ASSIGNED.
                if updated_ticket.assigned_to and updated_ticket.status == Ticket.Status.OPEN:
                    updated_ticket.status = Ticket.Status.ASSIGNED

                if updated_ticket.status == Ticket.Status.RESOLVED and not updated_ticket.resolved_at:
                    from django.utils import timezone
                    updated_ticket.resolved_at = timezone.now()
                if updated_ticket.status == Ticket.Status.CLOSED and not updated_ticket.closed_at:
                    from django.utils import timezone
                    updated_ticket.closed_at = timezone.now()

                updated_ticket.save()

                if updated_ticket.status != old_status:
                    TicketHistory.objects.create(
                        ticket=ticket, actor=request.user,
                        action=f"Status changed: {old_status} -> {updated_ticket.status}"
                    )
                if updated_ticket.priority != old_priority:
                    TicketHistory.objects.create(
                        ticket=ticket, actor=request.user,
                        action=f"Priority changed: {old_priority} -> {updated_ticket.priority}"
                    )
                if updated_ticket.assigned_to != old_assignee:
                    new_name = updated_ticket.assigned_to.username if updated_ticket.assigned_to else 'Unassigned'
                    TicketHistory.objects.create(
                        ticket=ticket, actor=request.user,
                        action=f"Reassigned to: {new_name}"
                    )
                messages.success(request, "Ticket updated.")
                return redirect('ticket_detail', pk=pk)

        elif form_name == 'close_ticket':
            # Employees can close their own resolved tickets ("customer confirms fixed").
            if ticket.created_by_id == request.user.id or _is_staff_role(request.user):
                from django.utils import timezone
                ticket.status = Ticket.Status.CLOSED
                ticket.closed_at = timezone.now()
                ticket.save()
                TicketHistory.objects.create(
                    ticket=ticket, actor=request.user, action="Ticket closed."
                )
                messages.success(request, f"Ticket {ticket.ticket_number} closed.")
                return redirect('ticket_detail', pk=pk)

    context = {
        'ticket': ticket,
        'comments': ticket.comments.select_related('author'),
        'attachments': ticket.attachments.select_related('uploaded_by'),
        'history': ticket.history.select_related('actor'),
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'agent_form': agent_form,
        'is_staff_role': _is_staff_role(request.user),
        'is_owner': ticket.created_by_id == request.user.id,
    }
    return render(request, 'tickets/ticket_detail.html', context)


# ---------------------------------------------------------------------------
# Admin-only views: agent management, category management, stats
# ---------------------------------------------------------------------------

def _admin_required(user):
    return hasattr(user, 'profile') and user.profile.is_admin_role


@login_required
def admin_stats(request):
    if not _admin_required(request.user):
        return HttpResponseForbidden("Admins only.")

    tickets = Ticket.objects.all()
    status_counts = tickets.values('status').annotate(count=Count('id')).order_by('status')
    priority_counts = tickets.values('priority').annotate(count=Count('id')).order_by('priority')
    category_counts = tickets.values('category__name').annotate(count=Count('id')).order_by('-count')
    agent_workload = (
        User.objects.filter(profile__role='AGENT')
        .annotate(
            open_count=Count('assigned_tickets', filter=~Q(assigned_tickets__status=Ticket.Status.CLOSED)),
            total_count=Count('assigned_tickets'),
        )
    )

    context = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.exclude(status=Ticket.Status.CLOSED).count(),
        'closed_tickets': tickets.filter(status=Ticket.Status.CLOSED).count(),
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'category_counts': category_counts,
        'agent_workload': agent_workload,
        'total_agents': User.objects.filter(profile__role='AGENT').count(),
        'total_employees': User.objects.filter(profile__role='EMPLOYEE').count(),
    }
    return render(request, 'tickets/admin_stats.html', context)


@login_required
def manage_agents(request):
    if not _admin_required(request.user):
        return HttpResponseForbidden("Admins only.")
    from accounts.forms import AgentCreationForm

    if request.method == 'POST':
        form = AgentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New support agent created.")
            return redirect('manage_agents')
    else:
        form = AgentCreationForm()

    agents = User.objects.filter(profile__role='AGENT').select_related('profile')
    return render(request, 'tickets/manage_agents.html', {'agents': agents, 'form': form})


@login_required
def toggle_agent_active(request, user_id):
    if not _admin_required(request.user):
        return HttpResponseForbidden("Admins only.")
    agent = get_object_or_404(User, pk=user_id, profile__role='AGENT')
    agent.profile.is_active_agent = not agent.profile.is_active_agent
    agent.profile.save()
    messages.success(request, f"{agent.username} is now {'active' if agent.profile.is_active_agent else 'inactive'}.")
    return redirect('manage_agents')


@login_required
def manage_categories(request):
    if not _admin_required(request.user):
        return HttpResponseForbidden("Admins only.")

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    categories = Category.objects.annotate(ticket_count=Count('tickets'))
    return render(request, 'tickets/manage_categories.html', {'categories': categories, 'form': form})


@login_required
def delete_category(request, pk):
    if not _admin_required(request.user):
        return HttpResponseForbidden("Admins only.")
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect('manage_categories')
