from django.shortcuts import render

def register_view(request):
    return render(request, 'accounts/register.html') # Trả về giao diện Đăng ký 

def login_view(request):
    return render(request, 'accounts/login.html') # Trả về giao diện Đăng nhập [cite: 61]