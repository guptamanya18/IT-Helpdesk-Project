from django import forms
from django.contrib.auth.models import User
from .models import Ticket, Comment, Attachment, Category


class TicketCreateForm(forms.ModelForm):
    """Used by Employees to raise a new ticket."""
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short summary, e.g. "VPN not connecting"'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the issue in detail...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Add a comment...'}),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AgentUpdateForm(forms.ModelForm):
    """
    Used by Support Agents on the ticket-detail page to change status,
    priority, resolution notes, and reassign to another agent.
    """
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='AGENT').order_by('username'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign to agent',
    )

    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to', 'resolution']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'resolution': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'How was this resolved?'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
