from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .form import *
from .models import *

# Create your views here.
@cache_page(2)

@login_required(login_url='login')
def HomePage(request):
    context = {}
    projects = Project.objects.all()
    context['projects'] = projects
    for project in projects:
        project.desc_singkat = ' '.join(project.deskripsi_project.split()[:22]) + '...'
    
    return render (request,'concept1/home.html', context)

def register(request):
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. You are now logged in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, '')
    else:
        form = RegistrationForm()

    return render(request, 'concept1/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found. Please register.")
            return redirect('login')

        username = user.username
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')

    return render(request, 'concept1/login.html')

def landingpage (request):
    return render(request, 'concept1/landing.html')

@login_required(login_url='login')
def LogoutPage (request):
    logout(request)
    return redirect('login')