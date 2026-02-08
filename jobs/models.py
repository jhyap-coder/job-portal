from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('IN', 'Internship'),
        ('CT', 'Contract'),
    )

    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=2, choices=JOB_TYPE_CHOICES)
    salary = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False) 

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    photo = models.ImageField(
        upload_to='application_photos/',
        blank=True,
        null=True
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True
    )

    applied_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )

    class Meta:
        unique_together = ('job', 'user')
        ordering = ['-applied_at']

    def clean(self):
        if self.user and (self.user.is_staff or self.user.is_superuser):
            raise ValidationError("Admins cannot apply for jobs.")

    def save(self, *args, **kwargs):
        if self.user:
            self.full_name = self.full_name or self.user.get_full_name()
            self.email = self.email or self.user.email
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} → {self.job.title} ({self.status})"




# Signal: automatically create UserProfile for each new User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role='jobseeker'
        )
        Profile.objects.create(user=instance)

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
