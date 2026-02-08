from django.contrib import admin
from .models import Job, JobApplication, ContactMessage



@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company_name',
        'location',
        'job_type',
        'is_active',
        'posted_at'
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'job',
        'user',
        'status',
        'email',
        'phone',
        'applied_at'
    )

    list_filter = ('status', 'job', 'applied_at')
    search_fields = ('user__username', 'email', 'full_name')
    list_editable = ('status',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "phone", "message")
    ordering = ("-created_at",)
    readonly_fields = ("name", "email", "phone", "message", "created_at")

    def has_add_permission(self, request):
        return False
