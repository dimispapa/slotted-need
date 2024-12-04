from django import forms
from django.contrib.auth.models import User, Group
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

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save the user first
        if commit:
            user.save()

        # Automatically add the user to Admin Group if is_staff=True
        if user.is_staff:
            try:
                admin_group = Group.objects.get(name='Admin Group')
                if not user.groups.filter(name='Admin Group').exists():
                    user.groups.add(admin_group)
            # raise validation error if the admin group does not exist
            except Group.DoesNotExist:
                raise ValidationError('Cannot set this user as Admin, '
                                      'because the Admin permissions group '
                                      'does not exist.'
                                      'Please check the Admin page or contact '
                                      'the app administrator.')

        return user


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

    def __init__(self, *args, **kwargs):
        # Expect the current user to be passed in the form's kwargs
        current_user = kwargs.pop('current_user', None)
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

        if current_user and not current_user.is_staff:
            # Remove the 'is_staff' field for non-admin users
            self.fields.pop('is_staff', None)

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save the user first
        if commit:
            user.save()

        # Automatically add the user to Admin Group if is_staff=True
        if user.is_staff:
            try:
                admin_group = Group.objects.get(name='Admin Group')
                if not user.groups.filter(name='Admin Group').exists():
                    user.groups.add(admin_group)
            # raise validation error if the admin group does not exist
            except Group.DoesNotExist:
                raise ValidationError('Cannot set this user as Admin, '
                                      'because the Admin permissions group '
                                      'does not exist.'
                                      'Please check the Admin page or contact '
                                      'the app administrator.')

        return user


class PasswordSetupForm(PasswordResetForm):
    def get_users(self, email):
        UserModel = get_user_model()
        inactive_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=False
        )
        return (u for u in inactive_users)
