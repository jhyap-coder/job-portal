from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView
from .forms import (
    RegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    JobApplicationForm,
    ProfilePhotoForm,
    JobCreateForm,
    CustomPasswordChangeForm
)
from .models import Profile, Job, JobApplication, UserProfile, ContactMessage

# ==========================
# HOME
# ==========================
def home(request):
    featured_jobs = Job.objects.filter(featured=True, is_active=True)
    return render(request, 'jobs/home.html', {'featured_jobs': featured_jobs})


# ==========================
# AUTHENTICATION
# ==========================
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Account created successfully.")
        return redirect('login')

    return render(request, 'jobs/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect('job_list')

        messages.error(request, "Invalid email or password.")

    return render(request, 'jobs/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


# ==========================
# PROFILE
# ==========================
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'jobs/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'jobs/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# ==========================
# JOB LIST & DETAILS
# ==========================
def job_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')

    jobs = Job.objects.filter(is_active=True)

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    applied_jobs = []
    if request.user.is_authenticated:
        applied_jobs = JobApplication.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'applied_jobs': applied_jobs
    })


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    return render(request, 'jobs/job_detail.html', {'job': job})


# ==========================
# APPLY JOB
# ==========================
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)

    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Admins cannot apply for jobs.")
        return redirect('job_list')

    user_profile = UserProfile.objects.filter(user=request.user).first()
    if not user_profile or user_profile.role != 'jobseeker':
        messages.error(request, "Only job seekers can apply for jobs.")
        return redirect('job_list')

    if JobApplication.objects.filter(job=job, user=request.user).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('job_list')

    if request.method == 'POST':
        application = JobApplication(user=request.user, job=job)
        form = JobApplicationForm(request.POST, request.FILES, instance=application)

        if form.is_valid():
            form.save()
            messages.success(request, "Application submitted successfully.")
            return redirect('job_list')
    else:
        form = JobApplicationForm(initial={
            'full_name': request.user.get_full_name(),
            'email': request.user.email
        })

    return render(request, 'jobs/apply_job.html', {
        'job': job,
        'form': form
    })


# ==========================
# MY APPLICATIONS
# ==========================
@login_required
def my_jobs(request):
    applications = JobApplication.objects.filter(
        user=request.user
    ).select_related('job')

    return render(request, 'jobs/my_jobs.html', {
        'applications': applications
    })


# ==========================
# ADMIN DASHBOARD
# ==========================
@staff_member_required(login_url='login')
def admin_dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProfilePhotoForm(instance=profile)

    total_users = User.objects.count()
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    pending_jobs = Job.objects.filter(is_active=False).count()

    context = {
        'profile': profile,
        'form': form,
        'total_users': total_users,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_jobs': pending_jobs,
    }

    return render(request, 'jobs/admin/admin_dashboard.html', context)


@staff_member_required
def admin_jobs(request):
    jobs = Job.objects.all()
    return render(request, "jobs/admin/admin_jobs.html", {"jobs": jobs})


@staff_member_required
def admin_create_job(request):
    if request.method == "POST":
        form = JobCreateForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job created successfully.")
            return redirect("admin_jobs")
    else:
        form = JobCreateForm()

    return render(request, "jobs/admin/admin_create_job.html", {"form": form})


@staff_member_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == "POST":
        form = JobCreateForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect("job_list")
    else:
        form = JobCreateForm(instance=job)

    return render(request, "jobs/admin/edit_job.html", {
        "form": form,
        "job": job
    })


@staff_member_required
def approve_job(request, id):
    job = get_object_or_404(Job, id=id)
    job.is_active = True
    job.save()
    return redirect("admin_jobs")


@staff_member_required
def reject_job(request, id):
    job = get_object_or_404(Job, id=id)
    job.is_active = False
    job.save()
    return redirect("admin_jobs")


@staff_member_required
def admin_applications(request):
    applications = JobApplication.objects.select_related("job", "user")
    return render(request, "jobs/admin/admin_applications.html", {"applications": applications})


@staff_member_required
def update_application_status(request, app_id, status):
    application = get_object_or_404(JobApplication, id=app_id)

    if status in dict(JobApplication.STATUS_CHOICES):
        application.status = status
        application.save()

    return redirect("admin_applications")


@staff_member_required
def admin_users(request):
    users = User.objects.all()
    return render(request, "jobs/admin/admin_users.html", {"users": users})


@staff_member_required
def toggle_user(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = not user.is_active
    user.save()
    return redirect("admin_users")


# ==========================
# CHANGE PASSWORD
# ==========================
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('password_change')

    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)


def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'jobs/change_password.html', {'form': form})


# ==========================
# CONTACT
# ==========================
def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message"),
        )
        messages.success(request, "Your message has been saved successfully.")
        return redirect("contact")

    return render(request, "jobs/contact.html")


@staff_member_required
def messages_list(request):
    messages_obj = ContactMessage.objects.all().order_by("-created_at")
    return render(request, "jobs/admin/message.html", {"messages": messages_obj})
