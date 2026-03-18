# account_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from .models import CustomUser

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user) 
            return redirect('home') 
        else:
            messages.error(request, 'The username or password is incorrect!')
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        fn = request.POST.get('full_name')
        u = request.POST.get('username')
        p = request.POST.get('password')
        rp = request.POST.get('re_password')

        if p != rp:
            messages.error(request, 'The confirmed password does not match!')
            return redirect('register')
            
        if CustomUser.objects.filter(username=u).exists():
            messages.error(request, 'This username is already taken!')
            return redirect('register')

        user = CustomUser.objects.create_user(username=u, password=p, full_name=fn)
        
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/register.html')

def logout_user(request):
    logout(request) 
    return redirect('login')


@login_required
@csrf_exempt
def add_account(request):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password != confirm:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username exists'})
        user = CustomUser.objects.create_user(username=username, password=password, full_name=full_name, role='user')
        return JsonResponse({'success': True, 'message': 'Created', 'id': user.id})
    return JsonResponse({'success': False, 'message': 'Invalid method'})


@login_required
@csrf_exempt
def edit_account(request):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    if request.method == 'POST':
        uid = request.POST.get('user_id')
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        try:
            user = CustomUser.objects.get(id=uid, role='user')
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        if CustomUser.objects.filter(username=username).exclude(id=uid).exists():
            return JsonResponse({'success': False, 'message': 'Username exists'})
        user.full_name = full_name
        user.username = username
        if pwd:
            user.password = make_password(pwd)
        user.save()
        return JsonResponse({'success': True, 'message': 'Updated'})
    return JsonResponse({'success': False, 'message': 'Invalid method'})


@login_required
@csrf_exempt
def delete_account(request):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    if request.method == 'POST':
        uid = request.POST.get('user_id')
        try:
            user = CustomUser.objects.get(id=uid, role='user')
            user.delete()
            return JsonResponse({'success': True, 'message': 'Deleted'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
    return JsonResponse({'success': False, 'message': 'Invalid method'})

@login_required
def account_list_view(request):
    if request.user.role != 'admin':
        return redirect('home')

    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.filter(role='user')
    if query:
        users = users.filter(Q(full_name__icontains=query) | Q(username__icontains=query))

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'accounts/account_list.html', context)