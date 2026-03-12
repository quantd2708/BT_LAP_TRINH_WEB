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
        # Lấy dữ liệu từ thẻ input name="username" và name="password"
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Hàm authenticate sẽ kiểm tra xem user/pass có đúng trong DB không
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user) # Tạo phiên đăng nhập (session)
            return redirect('home') # Chuyển hướng về trang chủ
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form đăng ký
        fn = request.POST.get('full_name')
        u = request.POST.get('username')
        p = request.POST.get('password')
        rp = request.POST.get('re_password')

        # Kiểm tra logic cơ bản
        if p != rp:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')
            
        if CustomUser.objects.filter(username=u).exists():
            messages.error(request, 'Tên đăng nhập này đã có người sử dụng!')
            return redirect('register')

        # Tạo tài khoản mới vào database
        user = CustomUser.objects.create_user(username=u, password=p, full_name=fn)
        
        # Đăng nhập luôn cho user sau khi tạo xong
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/register.html')

def logout_user(request):
    logout(request) # Xóa phiên đăng nhập
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
    # Chỉ admin mới được vào trang này
    if request.user.role != 'admin':
        return redirect('home')

    # Lấy danh sách user thường, hỗ trợ tìm kiếm
    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.filter(role='user')
    if query:
        users = users.filter(Q(full_name__icontains=query) | Q(username__icontains=query))

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'accounts/account_list.html', context)