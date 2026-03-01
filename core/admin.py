from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AdminProxy, Group, OgrenciProxy, Rating, Student, Survey

# Admin site başlıkları
admin.site.site_header = 'Gradia Yönetim Paneli'
admin.site.site_title = 'Gradia'
admin.site.index_title = 'Hoş Geldiniz'


class BaseStudentAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'ogrenci_no', 'group', 'is_active', 'date_joined')
    list_filter = ('group', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'ogrenci_no')
    ordering = ('last_name', 'first_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('Gradia', {'fields': ('group', 'ogrenci_no')}),
        ('Durum', {'fields': ('is_active', 'date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('Gradia', {'fields': ('group', 'ogrenci_no')}),
    )
    readonly_fields = ('date_joined', 'last_login')


@admin.register(OgrenciProxy)
class OgrenciAdmin(BaseStudentAdmin):
    list_display = ('username', 'get_full_name', 'ogrenci_no', 'group', 'is_active', 'date_joined')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    def save_model(self, request, obj, form, change):
        obj.is_staff = False
        super().save_model(request, obj, form, change)


@admin.register(AdminProxy)
class AdminUserAdmin(BaseStudentAdmin):
    list_display = ('username', 'get_full_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('Gradia', {'fields': ('group', 'ogrenci_no')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Durum', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('Yetkiler', {'fields': ('is_staff', 'is_superuser')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        super().save_model(request, obj, form, change)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_count')
    search_fields = ('name',)

    def student_count(self, obj):
        return obj.students.filter(is_staff=False).count()
    student_count.short_description = 'Öğrenci Sayısı'


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('lesson_name', 'is_active', 'rating_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('lesson_name',)

    def rating_count(self, obj):
        return obj.ratings.count()
    rating_count.short_description = 'Değerlendirme Sayısı'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('survey', 'rater', 'ratee', 'score', 'created_at')
    list_filter = ('survey', 'score')
    search_fields = ('rater__username', 'rater__first_name', 'ratee__username', 'ratee__first_name')
    raw_id_fields = ('rater', 'ratee')
    readonly_fields = ('created_at',)
