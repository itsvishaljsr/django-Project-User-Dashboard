import re
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import make_password, check_password

#To hadle signup user data
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone')
        category = request.POST.get('category')

        # Validation checks
        errors = []
        if not name or not email or not password or not confirm_password or not phone:
            errors.append('All fields are required.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already exists.')
        try:
            validate_email(email)
        except ValidationError:
            errors.append('Enter a valid email address.')
        
        # Validate Indian phone number (10 digits, starting with 6-9)
        if not re.match(r'^[6789]\d{9}$', phone):
            errors.append('Enter a valid Indian phone number.')

        if category not in ['restaurant', 'doctor', 'lawyer']:
            errors.append('Please select a valid category.')

        if errors:
            return render(request, 'signup.html', {
                'errors': errors,
                'name': name,
                'email': email,
                'phone': phone,
                'category': category
            })
        else:
            # If no errors, create the user
            user = User(name=name, email=email, password=make_password(password), phone=phone, category=category)
            user.save()
            messages.success(request, 'Signup successful. You can now log in.')
            return redirect('login')

    return render(request, 'signup.html')

#get user login by email and password
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
        else:
            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    request.session['name'] = user.name
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

#logout user and clear session
def logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

#get all user details and serach functionality 
def home(request):
    if 'name' not in request.session:
        return redirect('login')

    name = request.session['name']
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # Get all unique categories
    categories = User.objects.values_list('category', flat=True).distinct()

    # Initialize query set for users
    users = User.objects.all()

    # Apply category filter if provided
    if category_filter:
        users = users.filter(category=category_filter)
    # Apply keyword search if provided
    elif search_query:
        users = users.filter(
            name__icontains=search_query
        ) | users.filter(
            category__icontains=search_query
        )

    context = {
        'search_query': search_query,
        'categories': categories,
        'users': users
    }

    return render(request, 'home.html', context)