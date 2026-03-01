from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Group, Rating, Student, Survey


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'ogrenci_no', 'group', 'is_staff', 'is_active')
    list_filter = ('group', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'ogrenci_no')
    fieldsets = UserAdmin.fieldsets + (
        ('Gradia', {'fields': ('group', 'ogrenci_no')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Gradia', {'fields': ('group', 'ogrenci_no')}),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_count')
    search_fields = ('name',)

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Öğrenci Sayısı'


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('lesson_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('lesson_name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('survey', 'rater', 'ratee', 'score', 'created_at')
    list_filter = ('survey', 'score')
    search_fields = ('rater__username', 'ratee__username')
    raw_id_fields = ('rater', 'ratee')
