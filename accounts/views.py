from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import EmployeeSignUpForm


def signup(request):
    """Public self-registration - always creates an EMPLOYEE account."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = EmployeeSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmployeeSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
