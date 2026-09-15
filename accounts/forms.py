from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class EmployeeSignUpForm(UserCreationForm):
    """
    Public signup form. Anyone who registers here becomes an EMPLOYEE.
    Support Agents and Admins are created by an Admin from the admin
    panel / agent-management page instead -- that's a deliberate
    business rule, not an oversight (you don't want randoms signing
    themselves up as support staff).
    """
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.department = self.cleaned_data.get('department', '')
            user.profile.role = Profile.Role.EMPLOYEE
            user.profile.save()
        return user


class AgentCreationForm(UserCreationForm):
    """Used by Admins to create new Support Agent accounts."""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.department = self.cleaned_data.get('department', '')
            user.profile.role = Profile.Role.AGENT
            user.profile.save()
        return user
