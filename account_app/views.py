from django.shortcuts import render

def register_view(request):
    return render(request, 'accounts/register.html') # Trả về giao diện Đăng ký 

def login_view(request):
    return render(request, 'accounts/login.html') # Trả về giao diện Đăng nhập [cite: 61]

def account_list_view(request):
    # dummy user data
    users = [
        {'name': 'Nghiêm Thị Kim Quy', 'account': 'quynh@vngpt.vn', 'password': 'p@ss123'},
        {'name': 'Nguyễn Văn Mạnh', 'account': 'manhvn@vngpt.vn', 'password': 'manhvv@'},
        {'name': 'Hoàng Văn An', 'account': 'anvh@vngpt.vn', 'password': 'anhv8@'},
        {'name': 'Trần Nguyễn Hoàng', 'account': 'hoangtn@vngpt.vn', 'password': 'hoangtt!'},
    ]
    query = request.GET.get('q','')
    if query:
        users = [u for u in users if query.lower() in u['name'].lower() or query.lower() in u['account'].lower()]
    return render(request, 'accounts/account_list.html', {'users': users, 'query': query})
