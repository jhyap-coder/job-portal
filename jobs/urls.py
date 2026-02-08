from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    # ==========================
    # PUBLIC PAGES
    # ==========================
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),

    # ==========================
    # JOBS
    # ==========================
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    


    # ==========================
    # AUTHENTICATION
    # ==========================
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================
    # PROFILE
    # ==========================
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # ==========================
    # ADMIN DASHBOARD
    # ==========================
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Admin Jobs
    path('dashboard/admin/jobs/', views.admin_jobs, name='admin_jobs'),
    path('dashboard/admin/jobs/create/', views.admin_create_job, name='admin_create_job'),
    path('dashboard/admin/jobs/<int:id>/approve/', views.approve_job, name='approve_job'),
    path('dashboard/admin/jobs/<int:id>/reject/', views.reject_job, name='reject_job'),
    path('dashboard/admin/jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),

    # Admin Applications
    path('dashboard/admin/applications/', views.admin_applications, name='admin_applications'),
    path(
        'dashboard/admin/applications/<int:app_id>/<str:status>/',
        views.update_application_status,
        name='update_application_status'
    ),
   path("dashboard/admin/messages/", views.messages_list, name="admin_messages"),


    # Admin Users
    path('dashboard/admin/users/', views.admin_users, name='admin_users'),
    path('dashboard/admin/users/<int:id>/toggle/', views.toggle_user, name='toggle_user'),

    # Other URLs...
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='jobs/password_change.html',
        success_url=reverse_lazy('profile') 
    ), name='password_change'),

    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='jobs/password_change.html'
    ), name='password_change_done'),
]
