from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Profile, JobApplication, Job
from .models import Testimonial


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Email address'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded', 
                'placeholder': 'Username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border rounded', 
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full px-3 py-2 border rounded', 
                'placeholder': 'Confirm Password'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'phone', 'location', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded', 'rows': 3}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'phone', 'photo', 'resume']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'w-full'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'w-full'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Prefill full_name and email from logged-in user
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['email'].initial = user.email

        # Make photo optional
        self.fields['photo'].required = False

    # PDF validation for resume
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume and not resume.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed for resume.")
        return resume

class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'w-full'})
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and not photo.content_type.startswith('image/'):
            raise forms.ValidationError("Only image files are allowed.")
        return photo

class JobCreateForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "company_name",
            "location",
            "job_type",
            "salary",
            "description",
            "requirements",
            "featured",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={'placeholder': 'Enter job title', 'class': 'w-full border rounded px-3 py-2'}),
            "requirements": forms.Textarea(attrs={'placeholder': 'Enter company name', 'class': 'w-full border rounded px-3 py-2'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter job location', 'class': 'w-full border rounded px-3 py-2'}),
            'job_type': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'salary': forms.NumberInput(attrs={'placeholder': 'Enter salary', 'class': 'w-full border rounded px-3 py-2'}),
            'requirements': forms.Textarea(attrs={'placeholder': 'Enter job requirements', 'class': 'w-full border rounded px-3 py-2', 'rows': 4}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Enter company name', 'class': 'w-full border rounded px-3 py-2'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter company name', 'class': 'w-full border rounded px-3 py-2'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common_class = (
            "w-full px-4 py-3 pr-16 rounded-xl border border-gray-300 "
            "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 "
            "bg-white text-gray-800"
        )

        self.fields['old_password'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Enter your current password',
            'id': 'id_old_password'
        })

        self.fields['new_password1'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Enter your new password',
            'id': 'id_new_password1'
        })

        self.fields['new_password2'].widget.attrs.update({
            'class': common_class,
            'placeholder': 'Confirm your new password',
            'id': 'id_new_password2'
        })


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['designation', 'message']
        widgets = {
            'designation': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Your role, e.g. Frontend Developer'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Write your experience here...',
                'rows': 5
            }),
        }