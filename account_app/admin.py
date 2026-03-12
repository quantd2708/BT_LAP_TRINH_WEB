from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # 1. Thêm trường role và full_name vào màn hình chi tiết của từng User
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung (Tự thiết kế)', {'fields': ('full_name', 'role')}),
    )
    
    # 2. Hiển thị luôn cột role ra ngoài danh sách tổng cho dễ nhìn
    list_display = ('username', 'full_name', 'role', 'is_staff', 'is_superuser')
    
    # 3. Cho phép lọc danh sách theo role bên thanh menu phải
    list_filter = UserAdmin.list_filter + ('role',)

# Đăng ký CustomUser với giao diện CustomUserAdmin vừa tạo
admin.site.register(CustomUser, CustomUserAdmin)