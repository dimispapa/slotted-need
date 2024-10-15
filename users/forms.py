from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
        })
    )
    email2 = forms.EmailField(
        label='Confirm Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm email address',
        })
    )
    is_staff = forms.BooleanField(required=False, label='Admin User',
                                  help_text=('Designates whether the user can '
                                             'log into the admin site and '
                                             'access privileged areas'),)

    class Meta:
        model = User
        fields = ('email', 'email2', 'is_staff')

    def clean_email2(self):
        """
        Validate that the two email entries match and that the email is unique.
        """
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')

        if email and email2 and email != email2:
            raise ValidationError('Email addresses must match.')

        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')

        return email2


class CustomUserChangeForm(UserChangeForm):
    password = None  # Hide password field
    email = forms.EmailField(required=True)
    is_staff = forms.BooleanField(required=False, label='Admin User',
                                  help_text=('Designates whether the user can '
                                             'log into the admin site and '
                                             'access privileged areas'),)

    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff')


class PasswordSetupForm(PasswordResetForm):
    def get_users(self, email):
        UserModel = get_user_model()
        inactive_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=False
        )
        return (u for u in inactive_users)
