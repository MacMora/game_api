from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.videogames_model import VideoGame
from .models.user_model import CustomUser

# Register your models here.
admin.site.register(VideoGame)

# Configurar el admin para el modelo User personalizado
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_superuser', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_superuser', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )