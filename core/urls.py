from django.urls import path

from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Student views
    path('survey/', views.survey_view, name='survey'),
    path('profile/', views.profile_view, name='profile'),

    # Admin panel
    path('admin-panel/dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/groups/', views.groups_view, name='groups'),
    path('admin-panel/students/', views.students_view, name='students'),
    path('admin-panel/survey/', views.survey_list_view, name='survey_list'),
    path('admin-panel/results/', views.results_view, name='results'),
]
