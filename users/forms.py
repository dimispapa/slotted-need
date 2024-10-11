from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserChangeForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(label='Confirm Email', required=True)
    is_staff = forms.BooleanField(required=False, label='Admin User')

    class Meta:
        model = User
        fields = ('email', 'email2', 'is_staff')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email2 = cleaned_data.get('email2')

        # Check if emails match
        if email and email2 and email != email2:
            raise ValidationError('Email addresses must match.')

        # Check if email is already in use
        # if User.objects.filter(email=email).exists():
        #     raise ValidationError('A user with that email already exists.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email as username or generate a unique username
        user.username = self.cleaned_data['email']
        # User cannot log in until they set a password
        user.set_unusable_password()
        user.is_active = True  # Ensure the user is active
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = None  # Hide password field
    email = forms.EmailField(required=True)
    is_staff = forms.BooleanField(required=False, label='Admin Status')
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Groups'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff', 'groups')


class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        email = email.strip().lower()
        UserModel = get_user_model()
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True
        )
        return (u for u in active_users)
